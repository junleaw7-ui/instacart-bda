# Dataset

**Instacart Market Basket Analysis** (Kaggle, official Instacart 2017 release):
https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis

Raw CSVs are not committed to this repo (too large for git). Download the 6 files:

```
orders.csv
order_products__prior.csv
order_products__train.csv
products.csv
aisles.csv
departments.csv
```

and put them **directly in one flat folder** (not nested under an `archive/` or similarly-named subfolder created by unzipping the Kaggle download) — that folder should contain exactly the 6 CSVs listed above, nothing more. Then **tell the scripts where that folder is** — either:
- set the `INSTACART_DATA_DIR` environment variable to that folder's path, or
- pass `--data-dir <path>` on every script invocation

To set the environment variable, pick the command for your shell and replace the path with your own:

```powershell
# Windows PowerShell
$env:INSTACART_DATA_DIR = "C:\path\to\your\instacart-data"
```
```cmd
:: Windows cmd.exe
set INSTACART_DATA_DIR=C:\path\to\your\instacart-data
```
```bash
# bash / zsh (macOS/Linux)
export INSTACART_DATA_DIR=/path/to/your/instacart-data
```

These only persist for the current terminal session — set it again (or add it to your shell profile) each time you open a new terminal. To confirm it's set correctly before running anything:

```
python -c "import os; print(os.environ.get('INSTACART_DATA_DIR'))"
```

**You must set this yourself.** If `INSTACART_DATA_DIR` is unset and `--data-dir` isn't passed, the scripts fall back to a hardcoded default path (`C:\Users\USER\Desktop\Big Data\Instacart dataset`) — that's the original author's personal machine, not a placeholder or example to match. On any other machine that path won't exist, so scripts will fail (or, worse, silently read the wrong data if a similarly-named folder happens to exist). Do not rely on the default.

**If you forget this step, here's what you'll see:**
- `nonbigdata/` scripts (pandas): `FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Users\\USER\\Desktop\\Big Data\\Instacart dataset\\<some file>.csv'` (the exact filename depends on which script you ran — `orders.csv`, `products.csv`, or `order_products__prior.csv`). If the path in the error is `C:\Users\USER\Desktop\Big Data\Instacart dataset`, that's the original author's machine, not yours — it confirms `INSTACART_DATA_DIR` was never set (or `--data-dir` never passed); go back and set it.
- `bigdata/` scripts (PySpark): an `AnalysisException: Path does not exist: file:/C:/Users/USER/Desktop/Big Data/Instacart dataset/<some file>.csv` raised when the job runs (Spark reads CSVs lazily, so this can surface partway through a script rather than immediately at startup) — same cause, same fix.

For the Big Data pipeline on EMR, upload these files to S3 and point `--data-dir` at the `s3://` path instead.
