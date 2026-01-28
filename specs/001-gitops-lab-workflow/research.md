# Research: GitOps Workflow Lab for Azure ML

**Feature**: 001-gitops-lab-workflow
**Date**: 2026-01-27

## R1: Azure ML SDK v2 for Model Registration via MLflow

**Decision**: Use `azure-ai-ml` SDK v2 combined with `mlflow` for model registration. Authentication via `DefaultAzureCredential` (supports `az login` and Service Principal).

**Rationale**: The Azure ML SDK v2 (`azure-ai-ml`) is the current recommended SDK (v1 `azureml-core` is in maintenance mode). MLflow integration is native in Azure ML — when `mlflow.set_tracking_uri()` points to an Azure ML workspace, `mlflow.sklearn.log_model()` with `registered_model_name` automatically registers the model in the workspace's model registry.

**Alternatives considered**:
- `azureml-core` (v1 SDK): Deprecated for new projects. Would create tech debt.
- Pure MLflow without Azure ML SDK: Possible but requires manual tracking URI configuration and misses Data Asset management.
- Azure ML CLI v2: Too complex for a Python-focused lab; students should learn the SDK.

**Key implementation notes**:
- Connect to workspace: `MLClient(DefaultAzureCredential(), subscription_id, resource_group, workspace_name)`
- Set MLflow tracking: `mlflow.set_tracking_uri(ml_client.tracking_uri)`
- Register model: Use `mlflow.sklearn.log_model()` within a `mlflow.start_run()` context

## R2: Azure ML Pipeline for Inference (SDK v2 Command Job)

**Decision**: Use Azure ML SDK v2 `command()` job for the inference pipeline, not the `@pipeline` decorator or `ParallelRunStep`.

**Rationale**: A single command job is the simplest pipeline unit in Azure ML v2. It runs a Python script (`score.py`) on a compute cluster with defined inputs/outputs. For a beginner lab, this is far simpler than a multi-step pipeline or parallel batch inference. The student learns the core concept (submit code to cloud compute) without pipeline DAG complexity.

**Alternatives considered**:
- `@pipeline` decorator with multiple steps: Overkill for single inference task. Adds complexity without pedagogical value.
- `ParallelRunStep` / batch endpoint: Production-grade but complex. Requires understanding of mini-batches, scoring scripts with `init()` and `run()` hooks.
- Managed online endpoint: Requires deploying a web service — different scope from batch inference with CSV I/O.

**Key implementation notes**:
- Define environment: `Environment(image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04", conda_file="conda.yml")`
- Or use curated environment: `Environment(name="AzureML-sklearn-1.5-ubuntu22.04-py39-cpu")` (check availability)
- Better approach: Custom environment with explicit `conda.yml` in the lab for reproducibility
- Command job: `command(code="./src", command="python score.py ...", environment=env, compute="cpu-cluster", inputs={...}, outputs={...})`

## R3: GitHub Actions Reusable Workflow Pattern for Lab

**Decision**: Adapt all 5 reusable workflows from the parent repo, plus 2-3 caller workflows. Remove Databricks-specific logic. Add 1 optional deploy workflow for Azure ML.

**Rationale**: Students should see the same reusable workflow pattern used in production repos. The parent repo already has battle-tested workflow files. Simplifying them (removing Databricks validation, streamlining lint checks) makes them appropriate for the lab while maintaining the structural pattern.

**Adaptations from parent repo**:
- `reusable_lint.yml`: Keep all linters but simplify pip install (use `requirements.txt` from lab root). Remove requirements-change detection (not needed for lab).
- `reusable_semantic_version.yml`: Keep as-is (generic, no Databricks dependency).
- `reusable_create_tag.yml`: Keep as-is.
- `reusable_create_release.yml`: Keep as-is, update project_name.
- `reusable_pr_comment.yml`: Keep as-is.
- `ci.yml`: Call reusable_lint + reusable_pr_comment. Remove bundle validation job.
- `cd.yml`: Chain semantic_version -> create_tag -> create_release. Same as parent.
- `deploy_model.yml`: New. workflow_dispatch, uses Service Principal secrets, runs register_model.py.

## R4: Synthetic Data Generation for Churn Model

**Decision**: Use numpy random generators with fixed seed for reproducible synthetic churn data. No external datasets.

**Rationale**: Synthetic data avoids licensing issues, download dependencies, and ensures every student gets identical training results (fixed seed). The churn prediction domain is well-understood and produces intuitive features.

**Data generation approach**:
- 10,000 training samples, 500 inference samples
- Features correlate logically with churn (e.g., month-to-month contracts have higher churn probability)
- Use `numpy.random.default_rng(seed=42)` for reproducibility
- Encode categoricals using pandas `get_dummies()` or sklearn `OrdinalEncoder` before training

## R5: DefaultAzureCredential Authentication Chain

**Decision**: Use `DefaultAzureCredential` from `azure-identity` as the single authentication mechanism in all scripts.

**Rationale**: `DefaultAzureCredential` automatically tries multiple credential sources in order: environment variables (Service Principal), Azure CLI (`az login`), managed identity, etc. This means the same code works both locally (via `az login`) and in GitHub Actions (via Service Principal env vars) without code changes.

**Key implementation notes**:
- Install: `pip install azure-identity`
- Usage: `credential = DefaultAzureCredential()`
- For local: Student runs `az login` first
- For GitHub Actions: Set `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` as environment variables (from GitHub Secrets)
- No code changes needed between local and CI/CD execution

## R6: Azure ML Compute Cluster Configuration

**Decision**: Use a `Standard_DS2_v2` compute cluster with 0-1 nodes (auto-scale to zero when idle) to minimize costs.

**Rationale**: `Standard_DS2_v2` (2 vCPUs, 7 GB RAM) is sufficient for small-scale inference on 500 records. Auto-scale to 0 ensures no charges when idle. This VM size is available in Azure for Students free tier.

**Key implementation notes**:
- Create compute in script if not exists: `ml_client.compute.begin_create_or_update(AmlCompute(name="cpu-cluster", size="Standard_DS2_v2", min_instances=0, max_instances=1))`
- First job submission may take 3-5 minutes while compute provisions
- Tutorial should warn students about this wait time

## R7: Conda Environment for Azure ML Jobs

**Decision**: Include a `conda.yml` file in the lab that defines the exact Python environment for Azure ML compute jobs.

**Rationale**: Using a custom conda environment ensures reproducibility. Curated environments may change versions unexpectedly. A pinned `conda.yml` guarantees the scoring script runs with the same dependencies every time.

**conda.yml contents**:
```yaml
name: churn-inference
channels:
  - conda-forge
dependencies:
  - python=3.10
  - pip
  - pip:
    - scikit-learn==1.3.2
    - pandas==2.1.4
    - mlflow==2.9.2
    - azureml-mlflow==1.57.0
```
