# LLM Data Analysis Course

Course workspace for LLM-powered data analysis.

## Project structure

- `data/raw/` - raw data
- `data/processed/` - processed data
- `data/external/` - external data
- `notebooks/` - Jupyter notebooks
- `scripts/` - utility scripts
- `reports/` - analysis reports
- `prompts/` - prompts
- `src/` - source code
- `automation/` - automation code
- `database_assignments/` - PostgreSQL and database assignments
- `data_analysis_assignments/` - data analysis assignments

## Class startup (Chapters 01–04)

From this project folder, create and activate a Python virtual environment, then install the course packages:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The four sample CSV files needed for Chapters 03–04 are already in `data/raw/`.
If they ever need to be regenerated, run this command from the project root:

```powershell
python scripts/generate_sample_data.py
```

Open `notebooks/ch03_data_overview.ipynb` or `notebooks/ch04_pandas_basic.ipynb` only after selecting the `.venv` Python kernel.
