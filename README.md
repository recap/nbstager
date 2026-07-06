# NBStager

NBStager is a Jupyter Server extension for preparing notebook workspaces from launch URLs.

It can:

- clone a target Git repository;
- write launch parameters into a `.env` file;
- optionally install Python dependencies;
- optionally install R dependencies;
- optionally run a target `postBuild` script;
- stage data files from HTTP(S) URLs;
- redirect to a notebook in JupyterLab.

NBStager is designed to work in Binder, JupyterHub, and local JupyterLab environments.

## Install

From PyPI, once published:

```bash
pip install nbstager
```

From GitHub:

```bash
pip install git+https://github.com/recap/nbstager.git@v0.1.0
```

For development:

```bash
pip install -e .
```

The package includes a Jupyter Server config file that enables the extension automatically. If needed, enable it manually:

```bash
jupyter server extension enable --py nbstager --sys-prefix
```

Check:

```bash
jupyter server extension list
```

## Endpoint

NBStager registers this route:

```text
/launch
```

Example local URL:

```text
http://localhost:8888/launch?repo=https://github.com/recap/DataLens&branch=main&notebookpath=DataLens_EDA.ipynb
```

## Reserved query parameters

| Parameter | Required | Default | Description |
|---|---:|---|---|
| `repo` | yes | — | Git repository URL to clone. |
| `branch` | no | repository default | Branch, tag, or commit to checkout. |
| `urlpath` | no | `lab/tree` | Jupyter URL prefix used for redirect. |
| `notebookpath` | no | — | Notebook path relative to the target repository root. |
| `targetpath` | no | `workspace` | Workspace directory relative to the Jupyter server root. |
| `overwrite` | no | `1` | If `1`, clear the workspace before staging. |
| `cleanup` | no | `0` | If `1`, remove wrapper/source files from the server root. |
| `run_postbuild` | no | `0` | If `1`, run target `postBuild` after cloning. |
| `install_r_deps` | no | `0` | If `1`, install R deps from `install.R` or `DESCRIPTION`. |
| `data` | no | — | JSON object or array describing data files to download. |

All other query parameters are written to `.env`.

## Passing notebook parameters

```text
/launch?repo=https://github.com/recap/DataLens&CSV_URL=https://example.org/data.csv&DATASET_PID=doi:10.1234/example
```

creates:

```dotenv
CSV_URL=https://example.org/data.csv
DATASET_PID=doi:10.1234/example
```

inside:

```text
workspace/.env
```

Python notebooks can read it with:

```python
from dotenv import load_dotenv
import os

load_dotenv('.env')
print(os.getenv('CSV_URL'))
```

R notebooks can read it with:

```r
library(dotenv)
load_dot_env('.env')
Sys.getenv('CSV_URL')
```

## Data staging

The `data` parameter accepts JSON.

Decoded example:

```json
[
  {
    "url": "https://example.org/customers.csv",
    "path": "data/customers.csv"
  }
]
```

NBStager downloads the files into the workspace and writes:

```text
data_manifest.json
```

## Binder usage

A Binder wrapper repo can install NBStager with:

```text
nbstager @ git+https://github.com/recap/nbstager.git@v0.1.0
```

Then launch a target repository through the wrapper with:

```text
https://mybinder.org/v2/gh/OWNER/WRAPPER_REPO/main?urlpath=launch%3Frepo%3Dhttps%253A%252F%252Fgithub.com%252FOWNER%252FTARGET_REPO%26notebookpath%3Dnotebook.ipynb
```

## Development

```bash
pip install -e .
jupyter lab --ServerApp.token='' --ServerApp.log_level=DEBUG
```

Then open:

```text
http://localhost:8888/launch?repo=https://github.com/recap/DataLens&branch=main&notebookpath=DataLens_EDA.ipynb
```
