# NBStager

NBStager is a Jupyter Server extension for preparing notebook workspaces from launch URLs.

It can:

- write launch parameters into a `.env` file;
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
http://localhost:8888/launch?notebookpath=mynotebook.ipynb&DATASET_URL=https://example.org/data.csv
```

## Reserved query parameters

| Parameter      | Required | Default | Description                                             |
| -------------- | -------: | ------- | ------------------------------------------------------- |
| `notebookpath` |       no | —       | Notebook path relative to the target repository root.   |
| `data`         |       no | —       | JSON object or array describing data files to download. |

All other query parameters are written to `.env`.

## Passing notebook parameters

```text
/launch?notebookpath=mynotebook.ipynb&DATASET_URL=https://example.org/data.csv
```

creates:

```dotenv
DATASET_URL=https://example.org/data.csv
```

inside:

```text
.env
```

Python notebooks can read it with:

```python
from dotenv import load_dotenv
import os

load_dotenv('.env')
print(os.getenv('DATASET_URL'))
```

R notebooks can read it with:

```r
library(dotenv)
load_dot_env('.env')
Sys.getenv('DATASET_URL')
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

In Binder, install NBStager in your `requirements.txt`. Then launch a target repository through the wrapper with:

```text
https://mybinder.org/v2/gh/OWNER/WRAPPER_REPO/main?urlpath=launch?notebookpath=mynotebook.ipynb&DATASET_URL=https://example.org/data.csv
```

Working example:

```text
https://mybinder.org/v2/gh/recap/Datalens/dev?urlpath=launch%3Fdata%3D%255B%257B%2522url%2522%253A%2522https%253A%252F%252Fsamplelib.com%252Fcsv%252Fsample-edge-cases.csv%2522%252C%2522path%2522%253A%2522data%252Fsample-edge-cases.csv%2522%257D%255D%26repo%3Dhttps%253A%252F%252Fgithub.com%252Frecap%252FDatalens%26branch%3Ddev%26notebookpath%3DDataLens.ipynb%26DATASET_URL%3Dhttps%253A%252F%252Fdoi.org%252F10.5281%252Fzenodo.17708939
```

<!-- ## Development -->
<!---->
<!-- ```bash -->
<!-- pip install -e . -->
<!-- jupyter lab --ServerApp.token='' --ServerApp.log_level=DEBUG -->
<!-- ``` -->
<!---->
<!-- Then open: -->
<!---->
<!-- ```text -->
<!-- http://localhost:8888/launch?repo=https://github.com/recap/DataLens&branch=main&notebookpath=DataLens_EDA.ipynb -->
<!-- ``` -->
