"""Performance comparison: Big Data (PySpark, local[*]) vs. non-Big Data
(pandas/mlxtend/scikit-learn) implementations, at increasing data volumes.

Runs each implementation as a subprocess across a range of --n-orders values,
recording wall-clock time and peak resident memory (via psutil), and writes
the results to benchmark_results.csv.

NOTE: this runs Spark in local[*] mode on a single laptop (8GB RAM), not on
an EMR cluster -- it demonstrates the *scaling trend* and per-framework
overhead, not the final cluster-scale numbers. The real Big Data vs.
non-Big Data comparison for the report should be re-run on EMR with the
full 32M-row dataset once the cluster is provisioned.
"""
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import psutil

REPO_ROOT = Path(__file__).resolve().parent
NONBIGDATA_SRC = REPO_ROOT / "nonbigdata" / "src"
BIGDATA_SRC = REPO_ROOT / "bigdata" / "src"

ORDER_SCALES = [1_000, 5_000, 20_000, 100_000, 500_000]

JAVA_HOME = r"C:\Program Files\Microsoft\jdk-17.0.19.10-hotspot"


def run_and_measure(cmd: list[str], cwd: Path, env: dict | None = None) -> dict:
    # stdout/stderr go to a temp file, not subprocess.PIPE: Spark's verbose
    # console output (progress bars, WARN logs) can exceed the OS pipe buffer,
    # and polling proc.poll() without draining a PIPE deadlocks the child
    # once it fills up. A file has no such limit.
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".log", delete=False) as logfile:
        log_path = Path(logfile.name)
        start = time.perf_counter()
        proc = psutil.Popen(cmd, cwd=str(cwd), env=env, stdout=logfile, stderr=subprocess.STDOUT)

        peak_rss = 0
        while proc.poll() is None:
            try:
                rss = proc.memory_info().rss
                for child in proc.children(recursive=True):
                    try:
                        rss += child.memory_info().rss
                    except psutil.NoSuchProcess:
                        pass
                peak_rss = max(peak_rss, rss)
            except psutil.NoSuchProcess:
                break
            time.sleep(0.2)

        proc.wait()
        elapsed = time.perf_counter() - start

    stdout = log_path.read_text(errors="replace")
    for attempt in range(5):
        try:
            log_path.unlink(missing_ok=True)
            break
        except PermissionError:
            # A grandchild process (e.g. Spark's JVM) can hold the file
            # handle open briefly after the direct child has exited on Windows.
            time.sleep(1)
    return {
        "elapsed_sec": round(elapsed, 2),
        "peak_rss_mb": round(peak_rss / (1024 * 1024), 1),
        "returncode": proc.returncode,
        "stdout_tail": "\n".join(stdout.strip().splitlines()[-6:]) if stdout else "",
    }


def spark_env():
    import os

    env = os.environ.copy()
    env["JAVA_HOME"] = JAVA_HOME
    env["PATH"] = JAVA_HOME + r"\bin;" + env.get("PATH", "")
    return env


def main():
    results = []

    for n in ORDER_SCALES:
        print(f"\n=== n_orders={n} ===")

        print("  non-bigdata fpgrowth...")
        r = run_and_measure(
            [sys.executable, "fpgrowth_local.py", "--n-orders", str(n), "--min-support", "0.02"],
            cwd=NONBIGDATA_SRC,
        )
        results.append({"algorithm": "fpgrowth", "implementation": "nonbigdata", "n_orders": n, **r})
        print(f"    {r['elapsed_sec']}s, {r['peak_rss_mb']}MB, rc={r['returncode']}")

        print("  bigdata fpgrowth (spark local[*])...")
        r = run_and_measure(
            [sys.executable, "fpgrowth_spark.py", "--n-orders", str(n), "--min-support", "0.02"],
            cwd=BIGDATA_SRC,
            env=spark_env(),
        )
        results.append({"algorithm": "fpgrowth", "implementation": "bigdata", "n_orders": n, **r})
        print(f"    {r['elapsed_sec']}s, {r['peak_rss_mb']}MB, rc={r['returncode']}")

        print("  non-bigdata kmeans...")
        r = run_and_measure(
            [sys.executable, "kmeans_local.py", "--n-orders", str(n)],
            cwd=NONBIGDATA_SRC,
        )
        results.append({"algorithm": "kmeans", "implementation": "nonbigdata", "n_orders": n, **r})
        print(f"    {r['elapsed_sec']}s, {r['peak_rss_mb']}MB, rc={r['returncode']}")

        print("  bigdata kmeans (spark local[*])...")
        r = run_and_measure(
            [sys.executable, "kmeans_spark.py", "--n-orders", str(n)],
            cwd=BIGDATA_SRC,
            env=spark_env(),
        )
        results.append({"algorithm": "kmeans", "implementation": "bigdata", "n_orders": n, **r})
        print(f"    {r['elapsed_sec']}s, {r['peak_rss_mb']}MB, rc={r['returncode']}")

    import pandas as pd

    df = pd.DataFrame(results)
    out_path = REPO_ROOT / "benchmark_results.csv"
    df.to_csv(out_path, index=False)
    print(f"\nSaved results to {out_path}")
    print(df[["algorithm", "implementation", "n_orders", "elapsed_sec", "peak_rss_mb", "returncode"]].to_string(index=False))


if __name__ == "__main__":
    main()
