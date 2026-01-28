"""Utilidades comunes para MLflow tracking en pipelines de ML."""

import mlflow
from mlflow.models.signature import infer_signature
from typing import Any, Dict, Optional
import pandas as pd


def setup_experiment(experiment_name: str, catalog: str = "mlops_course") -> str:
    """
    Configura el experimento de MLflow en Unity Catalog.

    Args:
        experiment_name: Nombre del experimento
        catalog: Nombre del catálogo de Unity Catalog

    Returns:
        ID del experimento configurado
    """
    experiment_path = f"/Users/{experiment_name}"
    mlflow.set_experiment(experiment_path)

    # Configurar registry en Unity Catalog
    mlflow.set_registry_uri("databricks-uc")

    experiment = mlflow.get_experiment_by_name(experiment_path)
    return experiment.experiment_id


def log_model_with_signature(
    model: Any,
    model_name: str,
    X_sample: pd.DataFrame,
    y_sample: pd.Series,
    artifact_path: str = "model",
    registered_model_name: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
) -> mlflow.models.model.ModelInfo:
    """
    Registra un modelo con signature inferida automáticamente.

    Args:
        model: Modelo entrenado (sklearn, xgboost, etc.)
        model_name: Nombre descriptivo del modelo
        X_sample: Muestra de features para inferir signature
        y_sample: Muestra de target para inferir signature
        artifact_path: Path del artefacto en MLflow
        registered_model_name: Nombre para registrar en Model Registry
        tags: Tags adicionales para el modelo

    Returns:
        ModelInfo del modelo registrado
    """
    # Inferir signature
    predictions = model.predict(X_sample)
    signature = infer_signature(X_sample, predictions)

    # Configurar tags
    model_tags = {"model_name": model_name}
    if tags:
        model_tags.update(tags)

    # Log del modelo
    model_info = mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path=artifact_path,
        signature=signature,
        registered_model_name=registered_model_name,
    )

    # Agregar tags
    for key, value in model_tags.items():
        mlflow.set_tag(key, value)

    return model_info


def log_metrics(metrics: Dict[str, float], step: Optional[int] = None) -> None:
    """
    Registra métricas en el run activo.

    Args:
        metrics: Diccionario de métricas a registrar
        step: Paso opcional para métricas con series temporales
    """
    for name, value in metrics.items():
        mlflow.log_metric(name, value, step=step)


def log_params(params: Dict[str, Any]) -> None:
    """
    Registra parámetros en el run activo.

    Args:
        params: Diccionario de parámetros a registrar
    """
    mlflow.log_params(params)


def get_latest_model_version(
    model_name: str, catalog: str = "mlops_course", schema: str = "models"
) -> str:
    """
    Obtiene la última versión de un modelo en Unity Catalog.

    Args:
        model_name: Nombre del modelo
        catalog: Catálogo de Unity Catalog
        schema: Schema donde está registrado el modelo

    Returns:
        URI del modelo más reciente
    """
    from mlflow import MlflowClient

    client = MlflowClient()
    full_model_name = f"{catalog}.{schema}.{model_name}"

    versions = client.search_model_versions(f"name='{full_model_name}'")
    if not versions:
        raise ValueError(f"No se encontró el modelo: {full_model_name}")

    latest = max(versions, key=lambda v: int(v.version))
    return f"models:/{full_model_name}/{latest.version}"
