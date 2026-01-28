# Databricks notebook source
# MAGIC %md
# MAGIC # Campaign One - Step 01: Build Universe
# MAGIC
# MAGIC Construye el universo de datos para el modelo de Churn.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuración

# COMMAND ----------

from pyspark.sql import functions as F

# Parámetros del pipeline
CATALOG = spark.conf.get("catalog_name", "mlops_course")
BRONZE_SCHEMA = spark.conf.get("schema_bronze", "bronze")
SILVER_SCHEMA = spark.conf.get("schema_silver", "silver")
GOLD_SCHEMA = spark.conf.get("schema_gold", "gold")

# Parámetros del experimento
CAMPAIGN_ID = "campaign_one"
RUN_DATE = (
    dbutils.widgets.get("run_date") if "run_date" in dbutils.widgets.getAll() else None
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Leer datos desde Unity Catalog

# COMMAND ----------

# Leer features desde Gold layer
features_df = spark.table(f"{CATALOG}.{GOLD_SCHEMA}.churn_features")

print(f"Total de registros en features: {features_df.count()}")
display(features_df.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Filtrar universo para esta campaña

# COMMAND ----------

# Definir criterios del universo para Campaign One
# Ejemplo: Solo clientes activos con más de 3 meses de tenure
universe_df = features_df.filter(
    (F.col("churned") == 0)  # Solo clientes activos para scoring
    & (F.col("tenure_months") >= 3)  # Con suficiente historia
)

print(f"Universo filtrado: {universe_df.count()} clientes")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Guardar universo para siguiente paso

# COMMAND ----------

# Escribir a tabla temporal para el pipeline
output_table = f"{CATALOG}.{SILVER_SCHEMA}.campaign_one_universe"

universe_df.write.mode("overwrite").saveAsTable(output_table)

print(f"✅ Universo guardado en: {output_table}")

# COMMAND ----------

# Retornar métricas para logging
dbutils.notebook.exit(
    {
        "status": "success",
        "records_processed": universe_df.count(),
        "output_table": output_table,
        "campaign_id": CAMPAIGN_ID,
    }
)
