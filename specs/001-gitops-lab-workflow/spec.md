# Feature Specification: GitOps Workflow Lab for Azure ML

**Feature Branch**: `001-gitops-lab-workflow`
**Created**: 2026-01-27
**Status**: Draft
**Input**: User description: "Crear una carpeta labs con un lab de GitOps workflow para Azure, incluyendo CI/CD, despliegue de modelo en MLflow, pipeline de inferencia en Azure ML, tutorial completo para principiantes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Alumno configura repositorio y ejecuta GitOps workflow (Priority: P1)

Un alumno principiante crea un nuevo repositorio en GitHub, copia el contenido del lab, y ejecuta exitosamente un flujo completo de GitOps: crear una rama feature, hacer un pull request que dispare CI (lint + validaciones), y al hacer merge a main se genere automáticamente una versión semántica, un tag, y un release en GitHub.

**Why this priority**: Es la base fundamental del lab. Sin entender el flujo GitOps, los pasos posteriores (despliegue de modelo, pipelines) no tienen sentido. Además, el alumno verifica que su entorno GitHub está correctamente configurado.

**Independent Test**: El alumno puede verificar que en la pestaña Actions de su repositorio aparecen los workflows ejecutados exitosamente, y en la sección Releases aparece la primera versión publicada.

**Acceptance Scenarios**:

1. **Given** el alumno tiene una cuenta de GitHub y acceso a un terminal, **When** sigue las instrucciones para crear el repositorio y copiar el contenido del lab, **Then** el repositorio queda configurado con los workflows de CI/CD, archivos Python semilla, y la estructura de carpetas completa.
2. **Given** el repositorio está creado con los workflows, **When** el alumno crea una rama, modifica un archivo Python, y abre un Pull Request hacia main, **Then** el workflow de CI se ejecuta automáticamente validando lint (Black, Flake8, isort, Pylint, MyPy) y publica un comentario en el PR con los resultados.
3. **Given** el PR ha pasado el CI exitosamente, **When** el alumno hace merge a main con un mensaje que siga conventional commits (por ejemplo `feat: add initial model scripts`), **Then** el workflow de CD genera automáticamente una versión semántica, crea un tag git, y publica un release en GitHub con los artifacts del proyecto.

---

### User Story 2 - Alumno entrena modelo localmente y genera artefacto (Priority: P2)

El alumno ejecuta un script Python en su computadora local que entrena un modelo de clasificación simple (churn prediction) usando datos sintéticos, y genera un archivo pickle del modelo entrenado que será utilizado en los pasos posteriores de despliegue a Azure ML.

**Why this priority**: Es el paso intermedio que conecta el flujo GitOps con Azure. El alumno necesita un modelo tangible para desplegar, y este paso le enseña cómo generar artefactos de ML localmente.

**Independent Test**: El alumno verifica que el script se ejecuta sin errores, que se genera un archivo `model.pkl` y un archivo `model_metadata.json`, y que puede cargar el modelo y hacer una predicción de prueba.

**Acceptance Scenarios**:

1. **Given** el alumno tiene Python 3.10+ instalado y ha ejecutado `pip install -r requirements.txt`, **When** ejecuta el script `scripts/train_model.py`, **Then** se genera un modelo de clasificación entrenado con datos sintéticos (10,000 registros), guardado como `artifacts/model.pkl`.
2. **Given** el modelo ha sido entrenado, **When** el alumno ejecuta el script `scripts/test_model.py`, **Then** se carga el modelo y se muestra una predicción de prueba con un CSV de ejemplo, confirmando que el modelo funciona correctamente antes de subirlo a Azure.

---

### User Story 3 - Alumno configura credenciales de Azure y despliega modelo en MLflow (Priority: P3)

El alumno configura los secretos de Azure en su repositorio de GitHub (o localmente), se conecta a su workspace de Azure ML, y despliega el modelo entrenado al registro de modelos de MLflow dentro de Azure ML, pudiendo verificar que el modelo aparece correctamente en la interfaz de Azure ML Studio.

**Why this priority**: Es el primer contacto del alumno con Azure ML y el despliegue real de un modelo. Requiere que el modelo local ya exista (P2) y que el repositorio esté configurado (P1).

**Independent Test**: El alumno puede abrir Azure ML Studio, navegar a la sección de Models, y ver el modelo registrado con su versión, métricas y signature.

**Acceptance Scenarios**:

1. **Given** el alumno tiene un workspace de Azure ML activo y Azure CLI instalado, **When** ejecuta `az login` en su terminal y se autentica con su cuenta de Azure, **Then** los scripts locales pueden conectarse al workspace de Azure ML usando la credencial interactiva (DefaultAzureCredential).
2. **Given** el alumno está autenticado via `az login` y el modelo existe como artefacto local, **When** ejecuta el script `scripts/register_model.py`, **Then** el modelo se registra en MLflow dentro del workspace de Azure ML con su signature, métricas (accuracy, precision, recall, f1-score), y metadata.
3. **Given** el alumno quiere automatizar el registro via GitHub Actions (sección bonus), **When** crea un Service Principal y configura las credenciales como GitHub Secrets (Tenant ID, Client ID, Client Secret, Subscription ID, Resource Group, Workspace Name), **Then** el workflow opcional puede autenticarse contra Azure ML.
3. **Given** el modelo está registrado en Azure ML, **When** el alumno navega a Azure ML Studio > Models, **Then** puede ver el modelo listado con su versión, fecha de registro, y artefactos asociados.

---

### User Story 4 - Alumno crea y ejecuta pipeline de inferencia en Azure ML (Priority: P4)

El alumno crea un archivo CSV con datos de entrada en su computadora local, lo sube a su workspace de Azure ML, y ejecuta un pipeline de inferencia que consume ese CSV, carga el modelo registrado, calcula probabilidades de churn, y produce un CSV de salida con las predicciones.

**Why this priority**: Es la tarea más compleja y avanzada del lab. Integra todos los conceptos anteriores (modelo registrado, Azure ML configurado) y demuestra un caso de uso de ML end-to-end.

**Independent Test**: El alumno puede descargar el CSV de output del pipeline desde Azure ML y verificar que contiene las columnas originales más una columna de probabilidad predicha.

**Acceptance Scenarios**:

1. **Given** el alumno tiene el script `scripts/create_inference_data.py`, **When** lo ejecuta localmente, **Then** se genera un archivo `data/inference_input.csv` con datos sintéticos de clientes (sin la columna target) listos para predicción.
2. **Given** el archivo CSV de inferencia existe localmente, **When** el alumno ejecuta el script `scripts/upload_data.py`, **Then** el CSV se sube como un Data Asset al workspace de Azure ML, visible en Azure ML Studio > Data.
3. **Given** los datos están en Azure ML y el modelo está registrado, **When** el alumno ejecuta el script `scripts/run_inference_pipeline.py` (o el workflow de GitHub Actions dispara el pipeline), **Then** Azure ML ejecuta un pipeline que: (a) lee el CSV de entrada, (b) carga el modelo registrado, (c) genera predicciones de probabilidad, (d) guarda un CSV de salida con las predicciones en el workspace.
4. **Given** el pipeline ha terminado exitosamente, **When** el alumno descarga el CSV de output, **Then** el archivo contiene todas las columnas originales más una columna `churn_probability` con valores entre 0 y 1 para cada registro.

---

### User Story 5 - Alumno consulta guía de creación de workspace Azure ML (Priority: P5)

Un alumno que aún no tiene un workspace de Azure ML consulta la sección complementaria del tutorial donde se explica paso a paso cómo crear uno desde el portal de Azure, incluyendo la creación de un Service Principal para autenticación automatizada.

**Why this priority**: Es contenido de apoyo. La mayoría de alumnos ya tendrán workspace, pero es necesario como referencia para quienes no lo han hecho. No bloquea las tareas anteriores si ya existe el workspace.

**Independent Test**: El alumno puede crear un workspace de Azure ML funcional siguiendo exclusivamente las instrucciones del tutorial, sin necesidad de buscar documentación externa.

**Acceptance Scenarios**:

1. **Given** el alumno tiene una cuenta de Azure con una suscripción activa, **When** sigue las instrucciones del apéndice del tutorial, **Then** crea exitosamente un Resource Group, un workspace de Azure ML, y un Service Principal con los permisos correctos.
2. **Given** el workspace y Service Principal están creados, **When** el alumno ejecuta el script de verificación `scripts/verify_azure_connection.py` con sus credenciales, **Then** el script confirma que la conexión al workspace es exitosa.

---

### Edge Cases

- ¿Qué pasa si el alumno no tiene Python 3.10+ instalado? El tutorial incluye instrucciones de instalación o indicación de versión mínima.
- ¿Qué pasa si el CI falla por errores de lint? El tutorial incluye una sección de troubleshooting explicando cómo corregir errores comunes de Black, Flake8, isort.
- ¿Qué pasa si las credenciales de Azure están mal configuradas? El script de verificación `verify_azure_connection.py` muestra mensajes de error descriptivos.
- ¿Qué pasa si el modelo no se registra correctamente en MLflow? El tutorial incluye pasos de depuración para verificar la conexión con Azure ML.
- ¿Qué pasa si el pipeline de inferencia falla? Se proporciona un checklist de verificación: datos subidos, modelo registrado, permisos correctos.
- ¿Qué pasa si el alumno ya tiene un workspace pero no un Service Principal? La sección de Azure incluye instrucciones específicas para crear solo el Service Principal.

## Clarifications

### Session 2026-01-27

- Q: Should model registration be done via local script, GitHub Actions workflow, or both? → A: Local script first (`register_model.py` executed by the student locally), with the GitHub Actions workflow shown as an optional bonus/advanced section.
- Q: Should the Azure ML inference pipeline be triggered from a local script, a GitHub Actions workflow, or both? → A: Local script only (`run_inference_pipeline.py` executed locally by the student).
- Q: How should students authenticate against Azure ML from local scripts? → A: Both documented. `az login` (interactive browser) as the primary/simple path for local scripts. Service Principal + `.env` as alternative, required for the CI/CD bonus workflow.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El lab DEBE incluir un directorio `labs/gitops-workflow/` con toda la estructura necesaria para que el alumno lo copie a un nuevo repositorio.
- **FR-002**: El lab DEBE contener archivos de GitHub Actions workflows adaptados para Azure (CI con lint, CD con versionado semántico + tag + release, y despliegue a Azure ML).
- **FR-003**: Los workflows de CI DEBEN validar código Python usando Black, Flake8, isort, Pylint y MyPy, siguiendo el patrón de los workflows existentes del repositorio.
- **FR-004**: El workflow de CD DEBE generar versión semántica basada en conventional commits, crear tag y release en GitHub, siguiendo el patrón existente.
- **FR-005**: El lab DEBE incluir un script Python `train_model.py` que entrene un modelo de clasificación de churn con datos sintéticos y genere un archivo pickle.
- **FR-006**: El lab DEBE incluir un script `test_model.py` que permita verificar que el modelo entrenado funciona correctamente con datos de prueba.
- **FR-007**: El lab DEBE incluir un script `register_model.py` que el alumno ejecuta localmente para registrar el modelo en MLflow dentro de un workspace de Azure ML usando credenciales configuradas. Este es el flujo principal del lab.
- **FR-008**: El lab DEBE incluir un script `create_inference_data.py` que genere un CSV de datos sintéticos para inferencia.
- **FR-009**: El lab DEBE incluir un script `upload_data.py` que suba el CSV al workspace de Azure ML como Data Asset.
- **FR-010**: El lab DEBE incluir un script `run_inference_pipeline.py` que el alumno ejecuta localmente para crear y ejecutar un pipeline de inferencia en Azure ML que lea un CSV de entrada, cargue el modelo registrado, genere predicciones, y guarde un CSV de salida con probabilidades. No se requiere workflow de GitHub Actions para este paso.
- **FR-011**: El lab DEBE incluir un script `verify_azure_connection.py` que valide que las credenciales de Azure están correctamente configuradas.
- **FR-012**: El lab DEBE incluir un tutorial en Markdown (`README.md`) completamente detallado, escrito en español, dirigido a principiantes, con instrucciones paso a paso para cada tarea del lab.
- **FR-013**: El tutorial DEBE incluir una sección complementaria (apéndice) explicando cómo crear un workspace de Azure ML desde cero, incluyendo Service Principal.
- **FR-014**: El lab DEBE incluir un archivo `requirements.txt` con todas las dependencias Python necesarias para ejecutar los scripts localmente y contra Azure.
- **FR-015**: El lab DEBE incluir un archivo `pyproject.toml` configurado con las reglas de lint que el CI valida, para que el código del alumno pase las validaciones.
- **FR-016**: Para la ejecución local, los scripts DEBEN autenticarse via `az login` (DefaultAzureCredential) como método principal. Para el workflow bonus de GitHub Actions, se DEBEN usar GitHub Secrets: `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `AZURE_ML_WORKSPACE_NAME`.
- **FR-017**: El lab DEBE incluir opcionalmente (sección bonus/avanzada) un workflow de GitHub Actions que automatice el registro del modelo en Azure ML, activado manualmente (workflow_dispatch) o al hacer merge a main tras cambios en los scripts de modelo.
- **FR-018**: El tutorial DEBE seguir un orden lógico: (1) crear repositorio, (2) configurar workflows/CI-CD, (3) entrenar modelo local, (4) configurar Azure, (5) desplegar modelo, (6) ejecutar pipeline de inferencia.

### Key Entities

- **Modelo de ML**: Modelo de clasificación binaria (churn prediction) entrenado con scikit-learn, almacenado como pickle y registrado en MLflow.
- **Dataset de entrenamiento**: Datos sintéticos generados programáticamente con features de cliente (tenure, monthly_charges, total_charges, contract_type, etc.) y target binario (churned).
- **Dataset de inferencia**: CSV sin columna target, con las mismas features del dataset de entrenamiento, usado como input del pipeline de inferencia.
- **Dataset de predicciones**: CSV de output del pipeline con las columnas originales más una columna `churn_probability`.
- **Workspace de Azure ML**: Entorno en la nube donde se registran modelos, datos, y se ejecutan pipelines.
- **Service Principal**: Identidad de aplicación en Azure AD usada para autenticación automatizada desde GitHub Actions.
- **GitHub Secrets**: Variables cifradas en el repositorio que almacenan credenciales de Azure para uso en workflows.
- **Workflow de CI**: Pipeline de integración continua que valida calidad de código en cada PR.
- **Workflow de CD**: Pipeline de entrega continua que genera versiones semánticas y releases al hacer merge a main.
- **Workflow de deploy**: Pipeline que despliega el modelo a Azure ML y/o ejecuta el pipeline de inferencia.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un alumno principiante puede completar la Parte 1 (GitOps workflow: crear repo, hacer PR, obtener release) siguiendo exclusivamente las instrucciones del tutorial sin consultar documentación externa.
- **SC-002**: El workflow de CI valida correctamente el código Python y reporta resultados en el PR en forma de comentario automático.
- **SC-003**: El workflow de CD genera una versión semántica válida, crea un tag git, y publica un release en GitHub con artifacts descargables.
- **SC-004**: El alumno puede entrenar el modelo localmente y obtener un archivo de modelo funcional que genere predicciones válidas.
- **SC-005**: El alumno puede configurar credenciales de Azure en GitHub Secrets y verificar la conexión usando el script de verificación.
- **SC-006**: El modelo se registra exitosamente en MLflow dentro de Azure ML, visible en Azure ML Studio con métricas y signature.
- **SC-007**: El pipeline de inferencia en Azure ML procesa un CSV de entrada y produce un CSV de salida con predicciones de probabilidad para todos los registros.
- **SC-008**: El tutorial cubre todos los escenarios de error comunes con instrucciones de troubleshooting para que el alumno pueda resolver problemas sin ayuda del instructor.

## Assumptions

- Los alumnos ya tienen una cuenta de GitHub con acceso a GitHub Actions (plan gratuito incluye Actions para repos públicos).
- Los alumnos tienen Python 3.10+ instalado localmente (se incluyen instrucciones de verificación).
- Los alumnos tienen acceso a una suscripción de Azure (puede ser Azure for Students o pay-as-you-go).
- Se asume que el workspace de Azure ML ya existe o el alumno seguirá el apéndice para crearlo.
- El modelo de ML será simple (scikit-learn LogisticRegression o RandomForest) para mantener el foco en el flujo GitOps/MLOps y no en la complejidad del modelo.
- Los datos son sintéticos para evitar dependencias de datasets externos.
- El tutorial está escrito en español dado que es para alumnos de UTEC.
- Los workflows se simplifican respecto a los del repositorio principal (se elimina la dependencia de Databricks) para enfocarse en Azure ML.
- El pipeline de inferencia de Azure ML usará un compute cluster simple (1 nodo) para mantener costos bajos.
