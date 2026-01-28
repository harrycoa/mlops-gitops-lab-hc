# Configuración del Sistema CI/CD

Guía completa para configurar el sistema de publicación de pipelines MLOps con Databricks Asset Bundles.

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Actions                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │     CI       │    │     CD       │    │   Deploy     │       │
│  │   Pipeline   │───▶│   Pipeline   │───▶│  Campaigns   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│        │                    │                    │               │
│        ▼                    ▼                    ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │    Lint      │    │   Version    │    │  Databricks  │       │
│  │  Validate    │    │   Release    │    │   Bundle     │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Databricks Workspace                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │    DEV      │    │    PROD     │    │   Unity     │          │
│  │  Workspace  │    │  Workspace  │    │  Catalog    │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Requisitos Previos

### 1. Databricks Workspace

- [ ] Workspace de Databricks con Unity Catalog habilitado
- [ ] Permisos de administrador o acceso a crear catálogos
- [ ] Databricks Runtime 14.0+ disponible

### 2. GitHub Repository

- [ ] Repositorio con branch protection en `main`
- [ ] Permisos para crear GitHub Actions secrets
- [ ] Permisos para crear GitHub Environments

### 3. Herramientas Locales

```bash
# Instalar Databricks CLI
pip install databricks-cli

# Verificar instalación
databricks --version
```

## Configuración Paso a Paso

### Paso 1: Configurar Secrets en GitHub

Ve a **Settings → Secrets and variables → Actions** y crea los siguientes secrets:

| Secret             | Descripción           | Ejemplo                                     |
| ------------------ | --------------------- | ------------------------------------------- |
| `DATABRICKS_HOST`  | URL del workspace     | `https://adb-123456.12.azuredatabricks.net` |
| `DATABRICKS_TOKEN` | Personal Access Token | `dapi...`                                   |

#### Cómo obtener el token de Databricks:

1. En Databricks, ve a **User Settings → Developer → Access tokens**
2. Click en **Generate new token**
3. Configura expiración (recomendado: 90 días)
4. Copia el token y guárdalo en GitHub Secrets

### Paso 2: Configurar Environments en GitHub

Ve a **Settings → Environments** y crea:

#### Environment: `dev`

- Sin protección adicional
- Secrets específicos (opcional): `DATABRICKS_HOST`, `DATABRICKS_TOKEN` para dev

#### Environment: `prod`

- **Required reviewers**: Añade reviewers para aprobación manual
- **Wait timer**: 5 minutos (opcional)
- Secrets específicos para producción

### Paso 3: Configurar Variables de Databricks

Edita `config/dev.yml`:

```yaml
variables:
  databricks_host: "https://adb-XXXXXXXXX.XX.azuredatabricks.net"
  catalog_name: "mlops_course_dev"
```

Edita `config/prod.yml`:

```yaml
variables:
  databricks_host: "https://adb-XXXXXXXXX.XX.azuredatabricks.net"
  catalog_name: "mlops_course"
  service_principal: "sp-mlops-prod"
```

### Paso 4: Configurar Unity Catalog

Ejecuta el notebook de setup en Databricks:

```bash
# Opción 1: Subir via CLI
databricks workspace import notebooks/00_setup_unity_catalog.py \
  /Shared/mlops_course/setup --language PYTHON

# Opción 2: Ejecutar directamente en la UI de Databricks
```

### Paso 5: Validar Configuración Local

```bash
# Configurar CLI
databricks configure --token

# Validar bundle
databricks bundle validate -t dev

# Deploy de prueba
databricks bundle deploy -t dev --dry-run
```

### Paso 6: Crear pyproject.toml

Crea `pyproject.toml` en la raíz del proyecto para configurar linters:

```toml
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88

[tool.pylint.messages_control]
disable = ["C0114", "C0115", "C0116"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
```

## Flujos de Trabajo

### CI Pipeline (Pull Requests)

```
PR abierto → Lint Check → Bundle Validate → PR Comment
```

**Trigger**: Cualquier PR a `main` o `develop`

**Checks**:

- Black (formateo)
- Flake8 (linting)
- isort (imports)
- Pylint (análisis estático)
- MyPy (tipos)
- Databricks bundle validate

### CD Pipeline (Releases)

```
Push a main → Semantic Version → Create Tag → Create Release
```

**Trigger**: Push a `main`

**Acciones**:

1. Calcula nueva versión semántica basada en commits
2. Crea tag en Git
3. Genera GitHub Release con ZIP del proyecto

### Deploy Pipelines (Asset Bundles)

```
Manual/Auto → Validate → Deploy → (Optional) Run Pipeline
```

**Triggers**:

- **Manual**: workflow_dispatch con selección de ambiente
- **Auto**: Push a `develop` con cambios en `src/components/run_campaign_*`

## Convenciones de Commits

Para que el versionado semántico funcione correctamente:

| Prefijo     | Tipo de cambio      | Versión       |
| ----------- | ------------------- | ------------- |
| `feat:`     | Nueva funcionalidad | MINOR (0.X.0) |
| `feat!:`    | Breaking change     | MAJOR (X.0.0) |
| `fix:`      | Corrección de bug   | PATCH (0.0.X) |
| `docs:`     | Documentación       | PATCH         |
| `style:`    | Formato de código   | PATCH         |
| `refactor:` | Refactorización     | PATCH         |
| `test:`     | Tests               | PATCH         |
| `chore:`    | Mantenimiento       | PATCH         |

**Ejemplos**:

```bash
git commit -m "feat: add customer segmentation model"
git commit -m "fix: correct inference pipeline timeout"
git commit -m "feat!: change Unity Catalog schema structure"
```

## Troubleshooting

### Error: "Bundle validation failed"

```bash
# Verificar sintaxis YAML
databricks bundle validate -t dev

# Ver detalles del error
databricks bundle validate -t dev --debug
```

### Error: "Authentication failed"

```bash
# Verificar token
databricks auth describe

# Re-configurar
databricks configure --token
```

### Error: "Catalog not found"

1. Verificar que Unity Catalog está habilitado
2. Ejecutar `notebooks/00_setup_unity_catalog.py`
3. Verificar permisos en el catálogo

### Error: "Workflow not found"

Los workflows reusables deben estar en `.github/` (no en `.github/workflows/` para este proyecto):

```
.github/
├── continuous_delivery.yml
├── continuous_integration.yml
├── promote_pipeline_campaign_one.yaml
├── promote_pipeline_campaign_two.yaml
├── reusable_create_release.yml
├── reusable_create_tag.yml
├── reusable_lint_python_validator.yml
├── reusable_pr_comment.yml
└── reusable_semantic_version.yml
```

## Checklist de Configuración

- [ ] Databricks workspace configurado con Unity Catalog
- [ ] GitHub Secrets configurados (`DATABRICKS_HOST`, `DATABRICKS_TOKEN`)
- [ ] GitHub Environments creados (`dev`, `prod`)
- [ ] `config/dev.yml` actualizado con URL del workspace
- [ ] `config/prod.yml` actualizado con URL del workspace
- [ ] `pyproject.toml` creado para configuración de linters
- [ ] Notebook de setup ejecutado en Databricks
- [ ] Bundle validado localmente (`databricks bundle validate`)
- [ ] Primer deploy exitoso a dev (`databricks bundle deploy -t dev`)

## Contacto y Soporte

Para dudas sobre el curso de MLOps UTEC, contactar al instructor.
