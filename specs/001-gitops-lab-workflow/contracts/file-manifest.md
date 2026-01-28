# File Manifest: GitOps Workflow Lab

**Feature**: 001-gitops-lab-workflow
**Date**: 2026-01-27

## Complete File Listing

All files to be created under `labs/gitops-workflow/`.

### Root Configuration Files

| File | Purpose | Source/Pattern |
|------|---------|---------------|
| `README.md` | Tutorial completo en español (6 partes + 2 apéndices) | New content |
| `requirements.txt` | Python dependencies for local execution | New |
| `pyproject.toml` | Lint config (Black, Flake8, isort, Pylint, MyPy) | Adapted from parent `pyproject.toml` |
| `conda.yml` | Azure ML compute environment definition | New |
| `.gitignore` | Ignore artifacts/, data/, .env, config.json, __pycache__ | New |

### GitHub Actions Workflows (`.github/workflows/`)

| File | Trigger | Purpose | Adapted From |
|------|---------|---------|-------------|
| `ci.yml` | PR to main | Lint validation + PR comment | `continuous_integration.yml` |
| `cd.yml` | Push to main | Semantic version + tag + release | `continuous_delivery.yml` |
| `deploy_model.yml` | workflow_dispatch (bonus) | Register model in Azure ML | New (uses SP secrets) |
| `reusable_lint.yml` | Called by ci.yml | Python lint checks | `reusable_lint_python_validator.yml` |
| `reusable_semantic_version.yml` | Called by cd.yml | Calculate semantic version | `reusable_semantic_version.yml` (as-is) |
| `reusable_create_tag.yml` | Called by cd.yml | Create git tag | `reusable_create_tag.yml` (as-is) |
| `reusable_create_release.yml` | Called by cd.yml | Create GitHub release | `reusable_create_release.yml` (as-is) |
| `reusable_pr_comment.yml` | Called by ci.yml | Post PR comment | `reusable_pr_comment.yml` (as-is) |

### Python Scripts (`scripts/`)

| File | Execution | Inputs | Outputs | Azure Required |
|------|-----------|--------|---------|----------------|
| `train_model.py` | Local | None (generates synthetic data) | `artifacts/model.pkl`, `artifacts/model_metadata.json` | No |
| `test_model.py` | Local | `artifacts/model.pkl` | Console output (predictions) | No |
| `create_inference_data.py` | Local | None (generates synthetic data) | `data/inference_input.csv` | No |
| `verify_azure_connection.py` | Local | config.json or CLI args | Console output (connection status) | Yes |
| `register_model.py` | Local | `artifacts/model.pkl`, config.json | Registered model in Azure ML | Yes |
| `upload_data.py` | Local | `data/inference_input.csv`, config.json | Data Asset in Azure ML | Yes |
| `run_inference_pipeline.py` | Local | config.json, model name, data asset name | Pipeline job in Azure ML, output CSV | Yes |

### Source Code (`src/`)

| File | Execution | Purpose |
|------|-----------|---------|
| `score.py` | Azure ML compute | Scoring script: loads model, reads CSV, outputs predictions CSV |

### Placeholder Directories

| Directory | Purpose |
|-----------|---------|
| `artifacts/.gitkeep` | Local model storage (gitignored contents) |
| `data/.gitkeep` | Local data storage (gitignored contents) |

## Dependency Map

```
train_model.py
  └── artifacts/model.pkl + model_metadata.json
       ├── test_model.py (verification)
       └── register_model.py (Azure ML registration)
            └── run_inference_pipeline.py (uses registered model)

create_inference_data.py
  └── data/inference_input.csv
       └── upload_data.py (Azure ML Data Asset)
            └── run_inference_pipeline.py (uses uploaded data)

verify_azure_connection.py (standalone, run anytime after az login)

score.py (used internally by Azure ML pipeline, not run directly)
```

## Interface Contracts

### train_model.py

```
Usage: python scripts/train_model.py [--seed 42] [--n-samples 10000] [--output-dir artifacts]
Exit: 0 = success, 1 = error
Output files:
  - artifacts/model.pkl (scikit-learn RandomForestClassifier)
  - artifacts/model_metadata.json (training metadata + metrics)
```

### test_model.py

```
Usage: python scripts/test_model.py [--model-path artifacts/model.pkl]
Exit: 0 = success (model works), 1 = error
Output: Console - sample predictions and model info
```

### create_inference_data.py

```
Usage: python scripts/create_inference_data.py [--seed 123] [--n-samples 500] [--output-dir data]
Exit: 0 = success, 1 = error
Output: data/inference_input.csv
```

### verify_azure_connection.py

```
Usage: python scripts/verify_azure_connection.py [--config config.json]
       python scripts/verify_azure_connection.py --subscription-id X --resource-group Y --workspace-name Z
Exit: 0 = connected, 1 = connection failed
Output: Console - workspace info or error message
```

### register_model.py

```
Usage: python scripts/register_model.py [--config config.json] [--model-path artifacts/model.pkl] [--model-name churn-prediction-model]
Exit: 0 = registered, 1 = error
Output: Console - registered model URI and version
```

### upload_data.py

```
Usage: python scripts/upload_data.py [--config config.json] [--file-path data/inference_input.csv] [--asset-name churn-inference-data]
Exit: 0 = uploaded, 1 = error
Output: Console - data asset URI
```

### run_inference_pipeline.py

```
Usage: python scripts/run_inference_pipeline.py [--config config.json] [--model-name churn-prediction-model] [--data-asset-name churn-inference-data] [--compute-name cpu-cluster]
Exit: 0 = pipeline submitted/completed, 1 = error
Output: Console - pipeline job URL, status updates, output file path
```

### score.py (Azure ML internal)

```
Usage: python score.py --input-path <path> --model-name <name> --output-path <path>
       (Executed inside Azure ML compute, not by student directly)
Reads: Input CSV from Azure ML mounted path
Writes: Output CSV with churn_probability column
```
