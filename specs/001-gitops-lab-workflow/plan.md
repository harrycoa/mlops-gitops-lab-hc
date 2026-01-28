# Implementation Plan: GitOps Workflow Lab for Azure ML

**Branch**: `001-gitops-lab-workflow` | **Date**: 2026-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-gitops-lab-workflow/spec.md`

## Summary

Create a self-contained lab directory (`labs/gitops-workflow/`) that teaches beginner students how to set up a complete GitOps workflow with GitHub Actions (CI/CD with semantic versioning), train and register an ML model in Azure ML via MLflow, and run an inference pipeline in Azure ML. The lab includes all source code (workflows, Python scripts), configuration files, and a comprehensive step-by-step tutorial in Spanish. The primary interaction path uses local scripts with `az login` authentication; GitHub Actions automation is documented as an optional bonus.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: scikit-learn, mlflow, azure-ai-ml, azure-identity, pandas, numpy, joblib
**Storage**: Local filesystem (pickle, CSV), Azure ML Data Assets, Azure ML Model Registry (MLflow)
**Testing**: Manual verification scripts (`test_model.py`, `verify_azure_connection.py`); CI linting via GitHub Actions
**Target Platform**: Local machine (macOS/Linux/Windows) + Azure ML cloud compute
**Project Type**: Single project (lab content directory)
**Performance Goals**: N/A (educational lab, not production system)
**Constraints**: Must work with Azure for Students free tier; compute cluster limited to 1 node; all data synthetic
**Scale/Scope**: Single lab for ~30 students; 7 Python scripts, 7 GitHub Actions workflows, 1 tutorial README

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Campaign-Based Pipeline Architecture | Deviation (Justified) | Lab uses a simplified 2-step pipeline (train + inference) instead of the full 5-stage campaign structure. This is intentional: the lab teaches GitOps/Azure ML fundamentals, not the full campaign architecture. Students learn the full campaign pattern in the main repo. |
| II. Unity Catalog First | N/A | Lab targets Azure ML, not Databricks. Unity Catalog is not applicable. |
| III. Databricks Asset Bundles | N/A | Lab uses GitHub Actions + Azure ML SDK, not DAB. Intentional simplification for Azure ML focus. |
| IV. MLflow Tracking Obligatorio | Compliant | Model registration uses MLflow with signature, metrics, and parameters logging. |
| V. Code Quality Gates | Compliant | CI workflow validates Black, Flake8, isort, Pylint, MyPy. pyproject.toml included with lint configs. |

**Gate Result**: PASS. Deviations from Principles I-III are justified because the lab is an independent educational resource targeting Azure ML (not Databricks). Principles IV and V are fully compliant.

## Project Structure

### Documentation (this feature)

```text
specs/001-gitops-lab-workflow/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── file-manifest.md # Complete file listing and descriptions
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
labs/gitops-workflow/
├── README.md                              # Tutorial completo en español
├── requirements.txt                       # Dependencias Python
├── pyproject.toml                         # Configuración de linters
├── .gitignore                             # Ignorar artifacts/, data/, .env
│
├── .github/
│   └── workflows/
│       ├── ci.yml                         # CI: lint on PR
│       ├── cd.yml                         # CD: semantic version + tag + release on merge to main
│       ├── deploy_model.yml               # (Bonus) Deploy model to Azure ML
│       ├── reusable_lint.yml              # Reusable: Python lint validator
│       ├── reusable_semantic_version.yml  # Reusable: semantic versioning
│       ├── reusable_create_tag.yml        # Reusable: git tag creation
│       ├── reusable_create_release.yml    # Reusable: GitHub release creation
│       └── reusable_pr_comment.yml        # Reusable: PR comment posting
│
├── scripts/
│   ├── train_model.py                     # Entrenar modelo con datos sintéticos
│   ├── test_model.py                      # Verificar modelo entrenado
│   ├── register_model.py                  # Registrar modelo en Azure ML / MLflow
│   ├── create_inference_data.py           # Generar CSV de inferencia
│   ├── upload_data.py                     # Subir CSV a Azure ML Data Asset
│   ├── run_inference_pipeline.py          # Crear y ejecutar pipeline de inferencia
│   └── verify_azure_connection.py         # Verificar conexión a Azure ML
│
├── src/
│   └── score.py                           # Script de scoring usado por el pipeline de Azure ML
│
├── artifacts/                             # (gitignored) Modelo entrenado
│   └── .gitkeep
│
└── data/                                  # (gitignored) Datos generados
    └── .gitkeep
```

**Structure Decision**: Single flat lab directory designed to be copied entirely into a new GitHub repository. The `.github/workflows/` subdirectory mirrors the parent repo's pattern but is simplified for Azure ML. Scripts are in `scripts/` (student-executed), and `src/` holds the scoring component used inside the Azure ML pipeline.

## Complexity Tracking

| Deviation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 8 workflow files in lab | Students need to see reusable workflow patterns (CI, CD, deploy) that mirror production repos | A single monolithic workflow would not teach modularity or reusability |
| Separate `src/score.py` | Azure ML pipeline components require a standalone scoring script separate from local scripts | Inline scoring in `run_inference_pipeline.py` is not supported by Azure ML component jobs |
| Two auth methods documented | `az login` for simplicity + Service Principal for bonus workflow automation | Only `az login` would not teach CI/CD authentication; only SP would be too complex for beginners |

## Design Decisions

### D1: Workflow Architecture

The lab includes 8 workflow files following the parent repo's reusable workflow pattern:
- **ci.yml**: Triggered on PR to main. Calls reusable_lint.yml for code quality, then reusable_pr_comment.yml for status reporting. Simplified from parent (no Databricks bundle validation).
- **cd.yml**: Triggered on push to main. Chains: reusable_semantic_version.yml -> reusable_create_tag.yml -> reusable_create_release.yml. Identical pattern to parent repo.
- **deploy_model.yml**: (Bonus) workflow_dispatch trigger. Uses Service Principal secrets to connect to Azure ML and register the model. Optional for students.
- **Reusable workflows**: Direct adaptations from parent repo, simplified where needed (e.g., lint removes Databricks-specific checks).

### D2: Python Script Design

All scripts follow a consistent pattern:
1. Parse arguments (or use defaults)
2. Print clear status messages in Spanish
3. Handle errors with descriptive messages
4. Return exit code 0 on success, 1 on failure

Key design choices:
- **train_model.py**: Uses scikit-learn RandomForestClassifier with synthetic churn data. Saves model as pickle + metadata JSON. Logs training metrics to console.
- **register_model.py**: Uses `azure-ai-ml` SDK + `mlflow` to connect to workspace via DefaultAzureCredential (az login). Requires `--subscription-id`, `--resource-group`, `--workspace-name` as CLI args (or from config file).
- **run_inference_pipeline.py**: Creates an Azure ML pipeline with a single command job that runs `src/score.py`. Uses the registered model and uploaded data asset as inputs.
- **score.py**: Standalone scoring script designed to run inside Azure ML compute. Reads input CSV path and model name from arguments, outputs predictions CSV.

### D3: Synthetic Data Schema

Churn prediction dataset with these features:
- `customer_id` (string): Unique identifier
- `tenure_months` (int): Months as customer (1-72)
- `monthly_charges` (float): Monthly bill amount (20-120)
- `total_charges` (float): Cumulative charges
- `contract_type` (categorical): "month-to-month", "one-year", "two-year"
- `internet_service` (categorical): "dsl", "fiber_optic", "no"
- `payment_method` (categorical): "electronic_check", "mailed_check", "bank_transfer", "credit_card"
- `num_support_tickets` (int): Support tickets filed (0-10)
- `churned` (binary): Target variable (0/1) - only in training data

### D4: Tutorial Structure (README.md)

The tutorial is organized into sequential parts with clear checkpoints:

1. **Prerequisitos** - Python, Git, GitHub account, Azure CLI
2. **Parte 1: Crear Repositorio** - Step-by-step repo creation and content setup
3. **Parte 2: GitOps Workflow** - Create branch, make PR, verify CI, merge, verify CD/release
4. **Parte 3: Entrenar Modelo Local** - Run train_model.py, verify with test_model.py
5. **Parte 4: Configurar Azure ML** - az login, verify connection
6. **Parte 5: Registrar Modelo en Azure ML** - Run register_model.py, verify in Studio
7. **Parte 6: Pipeline de Inferencia** - Create data, upload, run pipeline, download results
8. **Bonus: Automatización con GitHub Actions** - Service Principal, GitHub Secrets, deploy workflow
9. **Apéndice A: Crear Workspace Azure ML** - Portal walkthrough + Service Principal creation
10. **Apéndice B: Troubleshooting** - Common errors and solutions

### D5: Azure ML Pipeline Architecture

The inference pipeline is a single-step command job:
- **Compute**: Azure ML compute cluster (Standard_DS2_v2, 0-1 nodes, auto-scale)
- **Environment**: Curated Azure ML environment with scikit-learn + pandas
- **Input**: Registered Data Asset (CSV) + registered MLflow model name
- **Output**: CSV file with predictions saved to default datastore
- **Execution**: Student triggers via `run_inference_pipeline.py` which creates the pipeline definition and submits it

### D6: Configuration Management

Scripts use a `config.json` file (in lab root) for workspace connection parameters:
```json
{
  "subscription_id": "<your-subscription-id>",
  "resource_group": "<your-resource-group>",
  "workspace_name": "<your-workspace-name>"
}
```
This file is gitignored and created by the student following tutorial instructions. Scripts fall back to CLI arguments if config.json is not present.
