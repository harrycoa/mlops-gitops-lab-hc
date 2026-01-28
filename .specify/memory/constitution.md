<!--
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0 (initial ratification)
- Modified principles: N/A (new constitution)
- Added sections: Core Principles (5), Technology Stack, Development Workflow, Governance
- Removed sections: N/A
- Templates requiring updates: ✅ plan-template.md (aligned), ✅ spec-template.md (aligned), ✅ tasks-template.md (aligned)
- Follow-up TODOs: None
-->

# MLOps Template UTEC Constitution

## Core Principles

### I. Campaign-Based Pipeline Architecture

Cada modelo de ML DEBE organizarse como una "campaña" independiente con 5 etapas bien definidas:

1. **Build Universe** (`01_build_universe.py`): Construcción del universo de datos desde Unity Catalog
2. **Transformation** (`02_transformation.py`): Feature engineering y preparación de datos
3. **Inference** (`03_inference.py`): Ejecución del modelo para generar predicciones
4. **Evaluation** (`04_evaluation.py`): Evaluación de métricas y comparación con baseline
5. **Retrain** (`05_retrain.py`): Re-entrenamiento del modelo cuando las métricas lo justifican

**Rationale**: Esta estructura modular permite reutilización, debugging aislado, y paralelización en Databricks workflows.

### II. Unity Catalog First

- Todos los datos DEBEN leerse y escribirse a través de Unity Catalog (no paths directos a DBFS)
- Nomenclatura obligatoria: `<catalog>.<schema>.<table>` (ej: `mlops_course.bronze.transactions`)
- Las tablas DEBEN tener schemas definidos explícitamente
- Los modelos entrenados DEBEN registrarse en Unity Catalog Model Registry

**Rationale**: Unity Catalog garantiza gobernanza, linaje, y seguridad de datos en Databricks.

### III. Databricks Asset Bundles (DAB)

- Los pipelines DEBEN desplegarse usando Databricks Asset Bundles
- Configuración por ambiente: `dev.json`, `prod.json` en `/config/`
- Los bundles DEBEN ser idempotentes (re-deploy sin efectos secundarios)
- Estructura obligatoria del bundle:
  - `databricks.yml` en raíz del proyecto
  - Recursos declarados: workflows, jobs, clusters
  - Variables de ambiente separadas por target (dev/prod)

**Rationale**: DAB permite CI/CD nativo en Databricks con versionamiento de infraestructura.

### IV. MLflow Tracking Obligatorio

- Cada experimento DEBE registrar: parámetros, métricas, artefactos
- Los modelos DEBEN usar MLflow Model Signature
- Comparación de runs DEBE ser posible para justificar promoción a producción
- Integración con Unity Catalog Model Registry para versionamiento

**Rationale**: Trazabilidad completa del ciclo de vida del modelo es requisito para MLOps maduro.

### V. Code Quality Gates

- Todo código Python DEBE pasar los linters configurados: Black, Flake8, isort, Pylint, MyPy
- Docstrings obligatorios (Interrogate + Darglint)
- Semantic versioning en commits: `feat!:`, `feat:`, `fix:`, `docs:`, etc.
- PRs DEBEN pasar CI antes de merge

**Rationale**: Calidad de código es crítica para mantenibilidad en proyectos de ML de largo plazo.

## Technology Stack

| Componente       | Tecnología                         | Versión Mínima |
| ---------------- | ---------------------------------- | -------------- |
| **Platform**     | Databricks                         | Runtime 14.0+  |
| **Catalog**      | Unity Catalog                      | Enabled        |
| **Language**     | Python                             | 3.10+          |
| **ML Framework** | MLflow                             | 2.x            |
| **Deployment**   | Databricks Asset Bundles           | 0.200+         |
| **CI/CD**        | GitHub Actions                     | v4             |
| **Linting**      | Black, Flake8, isort, Pylint, MyPy | Latest         |

## Development Workflow

### Branch Strategy

- `main`: Producción, protegido, solo merge via PR
- `develop`: Integración, donde convergen features
- `feature/*`: Features individuales, desde develop
- `hotfix/*`: Fixes urgentes a producción

### Promotion Pipeline

1. **Dev**: Despliegue automático desde `develop` usando `config/dev.json`
2. **Prod**: Despliegue manual con aprobación desde `main` usando `config/prod.json`

### PR Requirements

- Todos los checks de linting DEBEN pasar
- Al menos 1 reviewer aprobado
- Descripción clara del cambio y su impacto
- Linked a issue/ticket cuando aplique

## Governance

- Esta constitución tiene precedencia sobre otras prácticas del proyecto
- Enmiendas requieren:
  1. Documentación del cambio propuesto
  2. Aprobación del instructor/lead
  3. Plan de migración si hay breaking changes
- Los PRs DEBEN verificar cumplimiento con estos principios
- Complejidad adicional DEBE justificarse explícitamente

**Version**: 1.0.0 | **Ratified**: 2026-01-13 | **Last Amended**: 2026-01-13
