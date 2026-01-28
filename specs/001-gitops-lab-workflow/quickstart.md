# Quickstart: GitOps Workflow Lab for Azure ML

**Feature**: 001-gitops-lab-workflow
**Date**: 2026-01-27

## Overview

This lab creates a self-contained directory (`labs/gitops-workflow/`) containing everything a beginner student needs to:
1. Set up a GitOps CI/CD workflow with GitHub Actions
2. Train and register an ML model in Azure ML
3. Run a batch inference pipeline in Azure ML

## Prerequisites

- Python 3.10+
- Git + GitHub account
- Azure CLI (`az`) installed
- Azure subscription with ML workspace (or follow Appendix A to create one)

## Quick Implementation Guide

### Step 1: Create Lab Directory Structure

Create `labs/gitops-workflow/` with subdirectories:
- `.github/workflows/` (8 workflow YAML files)
- `scripts/` (7 Python scripts)
- `src/` (1 scoring script)
- `artifacts/` (gitignored, model output)
- `data/` (gitignored, CSV files)

### Step 2: Create Workflow Files

Adapt from parent repo's `.github/workflows/`:
- `ci.yml` = simplified `continuous_integration.yml` (no Databricks)
- `cd.yml` = same pattern as `continuous_delivery.yml`
- `deploy_model.yml` = new (bonus, Azure ML deployment)
- 5 reusable workflows = direct copies with minor simplifications

### Step 3: Create Python Scripts

7 scripts in `scripts/` + 1 in `src/`:
1. `train_model.py` - Synthetic data + RandomForest training
2. `test_model.py` - Load and verify model
3. `register_model.py` - Azure ML + MLflow registration
4. `create_inference_data.py` - Generate inference CSV
5. `upload_data.py` - Upload to Azure ML Data Asset
6. `run_inference_pipeline.py` - Submit Azure ML pipeline job
7. `verify_azure_connection.py` - Test Azure connectivity
8. `src/score.py` - Scoring script for Azure ML compute

### Step 4: Create Configuration Files

- `requirements.txt` - All pip dependencies
- `pyproject.toml` - Lint configuration matching CI checks
- `conda.yml` - Azure ML compute environment
- `.gitignore` - Exclude artifacts/, data/, .env, config.json

### Step 5: Write Tutorial README.md

Comprehensive Spanish-language tutorial with 6 main parts + 2 appendices. Each part has numbered steps, expected outputs, and checkpoint verification.

## Key Technical Decisions

| Decision | Choice | Reference |
|----------|--------|-----------|
| ML Framework | scikit-learn RandomForest | research.md R4 |
| Azure SDK | azure-ai-ml v2 | research.md R1 |
| Auth (local) | az login / DefaultAzureCredential | research.md R5 |
| Auth (CI/CD) | Service Principal / GitHub Secrets | research.md R5 |
| Pipeline type | Single command job | research.md R2 |
| Compute | Standard_DS2_v2, 0-1 nodes | research.md R6 |
| Environment | Custom conda.yml | research.md R7 |

## File Count Summary

| Category | Count |
|----------|-------|
| Workflow YAMLs | 8 |
| Python scripts | 8 |
| Config files | 4 (requirements.txt, pyproject.toml, conda.yml, .gitignore) |
| Documentation | 1 (README.md) |
| Placeholder dirs | 2 (.gitkeep in artifacts/, data/) |
| **Total files** | **23** |
