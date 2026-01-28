# Tasks: GitOps Workflow Lab for Azure ML

**Input**: Design documents from `/specs/001-gitops-lab-workflow/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No automated tests requested. Verification is done via manual scripts (test_model.py, verify_azure_connection.py).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Lab root**: `labs/gitops-workflow/`
- **Workflows**: `labs/gitops-workflow/.github/workflows/`
- **Scripts**: `labs/gitops-workflow/scripts/`
- **Source**: `labs/gitops-workflow/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the lab directory structure and shared configuration files

- [x] T001 Create the lab directory structure with all subdirectories: `labs/gitops-workflow/`, `labs/gitops-workflow/.github/workflows/`, `labs/gitops-workflow/scripts/`, `labs/gitops-workflow/src/`, `labs/gitops-workflow/artifacts/`, `labs/gitops-workflow/data/`
- [x] T002 [P] Create `.gitkeep` placeholder files in `labs/gitops-workflow/artifacts/.gitkeep` and `labs/gitops-workflow/data/.gitkeep`
- [x] T003 [P] Create `.gitignore` in `labs/gitops-workflow/.gitignore` with rules to ignore: `artifacts/*.pkl`, `artifacts/*.json`, `data/*.csv`, `.env`, `config.json`, `__pycache__/`, `*.pyc`, `venv/`
- [x] T004 [P] Create `requirements.txt` in `labs/gitops-workflow/requirements.txt` with dependencies: scikit-learn, pandas, numpy, joblib, mlflow, azure-ai-ml, azure-identity, black, flake8, isort, pylint, mypy
- [x] T005 [P] Create `pyproject.toml` in `labs/gitops-workflow/pyproject.toml` adapted from parent repo's `pyproject.toml`, configured with Black (88 chars), Flake8, isort, Pylint, MyPy rules matching what the CI workflow validates
- [x] T006 [P] Create `conda.yml` in `labs/gitops-workflow/conda.yml` defining the Azure ML compute environment with python=3.10, scikit-learn==1.3.2, pandas==2.1.4, mlflow==2.9.2, azureml-mlflow==1.57.0 per research.md R7

**Checkpoint**: Lab directory exists with all configuration files ready

---

## Phase 2: Foundational (Reusable Workflow Files)

**Purpose**: Create all reusable GitHub Actions workflow files that are dependencies for the CI and CD caller workflows

**CRITICAL**: CI and CD workflows (US1) depend on these reusable workflows being in place

- [x] T007 [P] Create reusable lint workflow in `labs/gitops-workflow/.github/workflows/reusable_lint.yml` adapted from parent repo's `reusable_lint_python_validator.yml`. Simplify: remove Databricks-specific checks, keep Black/Flake8/isort/Pylint/MyPy checks, use `requirements.txt` from lab root, remove requirements-change detection logic
- [x] T008 [P] Create reusable semantic version workflow in `labs/gitops-workflow/.github/workflows/reusable_semantic_version.yml` copied from parent repo's `reusable_semantic_version.yml` with PaulHatch/semantic-version@v5.4.0, supporting feat:/feat!:/fix: conventional commit prefixes
- [x] T009 [P] Create reusable create tag workflow in `labs/gitops-workflow/.github/workflows/reusable_create_tag.yml` copied from parent repo's `reusable_create_tag.yml` using joutvhu/create-tag@v1.0.2
- [x] T010 [P] Create reusable create release workflow in `labs/gitops-workflow/.github/workflows/reusable_create_release.yml` copied from parent repo's `reusable_create_release.yml` using thedoctor0/zip-release@0.7.6 and softprops/action-gh-release@v1, update project_name to "gitops-lab"
- [x] T011 [P] Create reusable PR comment workflow in `labs/gitops-workflow/.github/workflows/reusable_pr_comment.yml` copied from parent repo's `reusable_pr_comment.yml` using mshick/add-pr-comment@v2.8.1

**Checkpoint**: All 5 reusable workflows ready. Caller workflows can now reference them.

---

## Phase 3: User Story 1 - GitOps Workflow (Priority: P1) MVP

**Goal**: Student creates repo, opens PR triggering CI (lint), merges to main triggering CD (semantic version + tag + release)

**Independent Test**: GitHub Actions tab shows successful CI run on PR and successful CD run on merge. Releases section shows v0.1.0

### Implementation for User Story 1

- [x] T012 [US1] Create CI workflow in `labs/gitops-workflow/.github/workflows/ci.yml` triggered on PR to main/develop. Must call `reusable_lint.yml` for code quality (Black, Flake8, isort, Pylint, MyPy) and `reusable_pr_comment.yml` to post results table. Follow same pattern as parent `continuous_integration.yml` but without validate_bundle job. Include concurrency group
- [x] T013 [US1] Create CD workflow in `labs/gitops-workflow/.github/workflows/cd.yml` triggered on push to main (paths-ignore: **.md, .gitignore). Must chain: reusable_semantic_version.yml -> reusable_create_tag.yml -> reusable_create_release.yml. Follow exact pattern from parent `continuous_delivery.yml`. Include concurrency group
- [x] T014 [P] [US1] Create a seed Python file in `labs/gitops-workflow/scripts/__init__.py` (empty) and ensure `labs/gitops-workflow/scripts/train_model.py` exists as a minimal placeholder (just docstring + pass) so students have a Python file to modify for their first PR. This file will be fully implemented in US2 but needs to exist for CI lint to have something to validate

**Checkpoint**: CI triggers on PR and validates Python lint. CD triggers on merge and creates semantic version + tag + release

---

## Phase 4: User Story 2 - Train Model Locally (Priority: P2)

**Goal**: Student runs train_model.py to generate model.pkl and model_metadata.json, then verifies with test_model.py

**Independent Test**: Running `python scripts/train_model.py` creates artifacts/model.pkl and artifacts/model_metadata.json. Running `python scripts/test_model.py` shows predictions

### Implementation for User Story 2

- [x] T015 [US2] Implement `labs/gitops-workflow/scripts/train_model.py` with: argparse (--seed 42, --n-samples 10000, --output-dir artifacts), synthetic churn data generation using numpy.random.default_rng(seed) per data-model.md E1 schema (customer_id, tenure_months, monthly_charges, total_charges, contract_type, internet_service, payment_method, num_support_tickets, churned), churn probability logic (higher for month-to-month, electronic_check, fiber_optic+tickets), pandas get_dummies for categoricals, scikit-learn RandomForestClassifier training, train/test split 80/20, metrics calculation (accuracy, precision, recall, f1), save model.pkl via joblib, save model_metadata.json with metrics/features/date. Print status messages in Spanish. Exit code 0/1
- [x] T016 [US2] Implement `labs/gitops-workflow/scripts/test_model.py` with: argparse (--model-path artifacts/model.pkl), load model with joblib, create 5 sample records matching training schema, run predictions, display results in formatted table with Spanish messages, show model info (type, num features). Exit code 0/1

**Checkpoint**: Student can train model locally and verify it works

---

## Phase 5: User Story 3 - Register Model in Azure ML (Priority: P3)

**Goal**: Student authenticates via az login, verifies Azure connection, and registers model in MLflow within Azure ML workspace

**Independent Test**: Model visible in Azure ML Studio > Models with version, metrics, and signature

**Dependencies**: Requires US2 completed (model.pkl must exist)

### Implementation for User Story 3

- [x] T017 [P] [US3] Implement `labs/gitops-workflow/scripts/verify_azure_connection.py` with: argparse (--config config.json OR --subscription-id/--resource-group/--workspace-name), load config from JSON file or CLI args, use DefaultAzureCredential from azure-identity, create MLClient from azure.ai.ml, attempt to connect and list workspace details (name, location, resource group), print success/failure with descriptive Spanish messages. Exit code 0/1
- [x] T018 [US3] Implement `labs/gitops-workflow/scripts/register_model.py` with: argparse (--config config.json, --model-path artifacts/model.pkl, --model-name churn-prediction-model), load config, use DefaultAzureCredential + MLClient to connect to workspace, set mlflow.set_tracking_uri(ml_client.tracking_uri), within mlflow.start_run(): log params (model_type, seed, n_samples from metadata), log metrics (accuracy, precision, recall, f1 from metadata), mlflow.sklearn.log_model with signature inferred from sample data and registered_model_name, print registered model URI and version in Spanish. Exit code 0/1

**Checkpoint**: Model registered in Azure ML, visible in Studio with metrics and signature

---

## Phase 6: User Story 4 - Inference Pipeline in Azure ML (Priority: P4)

**Goal**: Student generates inference CSV, uploads to Azure ML, runs inference pipeline, gets predictions CSV

**Independent Test**: Download output CSV from Azure ML containing original columns plus churn_probability

**Dependencies**: Requires US3 completed (model registered in Azure ML)

### Implementation for User Story 4

- [x] T019 [P] [US4] Implement `labs/gitops-workflow/scripts/create_inference_data.py` with: argparse (--seed 123, --n-samples 500, --output-dir data), generate synthetic data per data-model.md E2 schema (same features as training but NO churned column, customer_ids CUST-10001 to CUST-10500), save as data/inference_input.csv. Print count and sample rows in Spanish. Exit code 0/1
- [x] T020 [P] [US4] Implement `labs/gitops-workflow/src/score.py` with: argparse (--input-path, --model-name, --output-path), load model from MLflow model registry (mlflow.sklearn.load_model), read input CSV with pandas, apply same preprocessing as training (get_dummies for categoricals), predict_proba to get churn probability, add churn_probability column to original dataframe, save output CSV. Designed to run inside Azure ML compute. Print progress in Spanish
- [x] T021 [US4] Implement `labs/gitops-workflow/scripts/upload_data.py` with: argparse (--config config.json, --file-path data/inference_input.csv, --asset-name churn-inference-data), use DefaultAzureCredential + MLClient, create Data asset using ml_client.data.create_or_update() with type=uri_file, print data asset URI. Exit code 0/1
- [x] T022 [US4] Implement `labs/gitops-workflow/scripts/run_inference_pipeline.py` with: argparse (--config config.json, --model-name churn-prediction-model, --data-asset-name churn-inference-data, --compute-name cpu-cluster), use DefaultAzureCredential + MLClient, create or get compute cluster (Standard_DS2_v2, 0-1 nodes per research.md R6), create custom Environment from conda.yml, define command job that runs src/score.py with input data asset and model name, submit job, wait for completion with status polling, download output CSV to data/inference_output.csv. Print job URL and status in Spanish. Exit code 0/1

**Checkpoint**: Pipeline runs in Azure ML, output CSV with churn_probability downloaded locally

---

## Phase 7: User Story 5 - Azure ML Workspace Guide + Bonus (Priority: P5)

**Goal**: Tutorial appendices covering workspace creation and optional GitHub Actions deployment automation

**Independent Test**: Student without workspace can create one following appendix instructions

### Implementation for User Story 5

- [x] T023 [P] [US5] Create bonus deploy workflow in `labs/gitops-workflow/.github/workflows/deploy_model.yml` with: workflow_dispatch trigger, uses Service Principal GitHub Secrets (AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, AZURE_ML_WORKSPACE_NAME), set up Python 3.10, install requirements, run register_model.py using environment variables for auth. Include job summary with deployment status

**Checkpoint**: Bonus workflow available for students who want to automate model registration

---

## Phase 8: Tutorial README (Cross-Cutting)

**Purpose**: Comprehensive Spanish-language tutorial that ties all components together

- [x] T024 Write the complete tutorial in `labs/gitops-workflow/README.md` in Spanish with these sections per plan.md D4: (1) Prerequisitos - list Python 3.10+, Git, GitHub account, Azure CLI with install links and verification commands; (2) Parte 1: Crear Repositorio - step-by-step instructions to create new GitHub repo, clone locally, copy lab contents, initial commit with conventional commit message, push to GitHub; (3) Parte 2: GitOps Workflow - create feature branch, modify train_model.py placeholder, commit with `feat:` prefix, push, create PR, verify CI runs and PR comment appears, merge PR, verify CD creates tag and release, screenshots guidance of expected GitHub UI; (4) Parte 3: Entrenar Modelo Local - pip install requirements, run train_model.py, explain output, run test_model.py, explain predictions; (5) Parte 4: Configurar Azure ML - install Azure CLI, run az login, create config.json with subscription/resource-group/workspace-name placeholders, run verify_azure_connection.py; (6) Parte 5: Registrar Modelo en Azure ML - run register_model.py, explain MLflow integration, verify in Azure ML Studio with navigation instructions; (7) Parte 6: Pipeline de Inferencia - run create_inference_data.py, run upload_data.py, run run_inference_pipeline.py, wait for completion, explain output CSV; (8) Bonus: Automatizacion con GitHub Actions - explain Service Principal concept, az ad sp create instructions, configure 6 GitHub Secrets, trigger deploy_model.yml workflow_dispatch; (9) Apendice A: Crear Workspace Azure ML - Azure portal navigation, create Resource Group, create ML workspace, create Service Principal with az ad sp create-for-rbac, assign Contributor role, collect all credential values; (10) Apendice B: Troubleshooting - common CI lint errors and fixes (Black formatting, isort imports, Flake8 line length), Azure connection errors (wrong subscription, expired token, missing az login), model registration errors (wrong workspace, MLflow tracking URI), pipeline errors (compute not found, environment issues, data asset not found). Each section must include expected output examples, checkpoint verification steps, and next-step guidance. Use code blocks for all commands. Include a table of contents at the top

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 (directory must exist)
- **Phase 3 (US1 - GitOps)**: Depends on Phase 2 (reusable workflows must exist)
- **Phase 4 (US2 - Train Model)**: Depends on Phase 1 only (no workflow dependency for local scripts)
- **Phase 5 (US3 - Register Model)**: Depends on Phase 4 (model.pkl must exist)
- **Phase 6 (US4 - Inference Pipeline)**: Depends on Phase 5 (model registered in Azure ML)
- **Phase 7 (US5 - Bonus)**: Depends on Phase 2 (reusable workflows for deploy_model.yml)
- **Phase 8 (Tutorial)**: Depends on ALL previous phases (documents all components)

### User Story Dependencies

- **US1 (GitOps)**: Independent - only needs reusable workflows (Phase 2)
- **US2 (Train Model)**: Independent - only needs lab directory (Phase 1)
- **US3 (Register Model)**: Depends on US2 (needs model.pkl artifact)
- **US4 (Inference Pipeline)**: Depends on US3 (needs registered model in Azure ML)
- **US5 (Bonus/Workspace)**: Independent - supplementary content

### Within Each User Story

- Configuration files before scripts
- Local scripts before Azure scripts
- Core implementation before integration

### Parallel Opportunities

- Phase 1: T002, T003, T004, T005, T006 can all run in parallel
- Phase 2: T007, T008, T009, T010, T011 can all run in parallel
- Phase 3 + Phase 4: US1 (workflows) and US2 (train model) can run in parallel since they don't depend on each other
- Phase 6: T019 and T020 can run in parallel (different files, no dependency)
- Phase 7: T023 can run in parallel with Phase 6

---

## Parallel Example: Setup + Foundational

```text
# Launch all config files in parallel (Phase 1):
T002: Create .gitkeep files in artifacts/ and data/
T003: Create .gitignore in labs/gitops-workflow/
T004: Create requirements.txt
T005: Create pyproject.toml
T006: Create conda.yml

# Launch all reusable workflows in parallel (Phase 2):
T007: reusable_lint.yml
T008: reusable_semantic_version.yml
T009: reusable_create_tag.yml
T010: reusable_create_release.yml
T011: reusable_pr_comment.yml
```

## Parallel Example: US1 + US2

```text
# After Phase 2, these two stories can run simultaneously:
Stream A (US1): T012 (ci.yml) -> T013 (cd.yml) -> T014 (seed file)
Stream B (US2): T015 (train_model.py) -> T016 (test_model.py)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational reusable workflows (T007-T011)
3. Complete Phase 3: US1 GitOps workflows (T012-T014)
4. **STOP and VALIDATE**: Push to a test repo, create PR, verify CI runs, merge, verify release
5. This alone delivers a working GitOps lab

### Incremental Delivery

1. Setup + Foundational + US1 -> GitOps works (MVP)
2. Add US2 (train model) -> Students can train locally
3. Add US3 (register model) -> Students deploy to Azure ML
4. Add US4 (inference pipeline) -> Full end-to-end ML pipeline
5. Add US5 (bonus + appendices) -> Complete lab with extras
6. Write Tutorial (Phase 8) -> Documentation ties everything together

### Recommended Build Order

1. T001 -> T002-T006 (parallel) -> T007-T011 (parallel)
2. T012-T014 (US1) + T015-T016 (US2) in parallel
3. T017-T018 (US3) sequentially
4. T019-T020 (parallel) -> T021 -> T022 (US4)
5. T023 (US5)
6. T024 (Tutorial) last - needs all scripts finalized

---

## Notes

- All Python scripts must pass Black, Flake8, isort, Pylint, MyPy checks as configured in pyproject.toml
- All scripts print messages in Spanish for the target audience (UTEC students)
- All scripts use argparse with sensible defaults so they work with zero configuration
- Azure scripts support both config.json and CLI arguments for workspace connection
- The tutorial (T024) is the largest single task and should be written last to reference final script behavior
- Workflow files are adapted from the parent repo at `.github/workflows/` - reference those files directly during implementation
