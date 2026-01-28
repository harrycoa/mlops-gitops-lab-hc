# Databricks notebook source
# MAGIC %md
# MAGIC # Setup Unity Catalog para MLOps Course
# MAGIC
# MAGIC Este notebook configura el catálogo, schemas y datos de ejemplo para el curso de MLOps.
# MAGIC
# MAGIC ## Estructura de datos (Medallion Architecture):
# MAGIC - **Bronze**: Datos crudos ingestados
# MAGIC - **Silver**: Datos limpios y transformados
# MAGIC - **Gold**: Datos agregados listos para ML

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuración inicial

# COMMAND ----------

# Parámetros configurables
CATALOG_NAME = "mlops_course"
BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Crear Catálogo y Schemas

# COMMAND ----------

# Crear catálogo (requiere permisos de admin)
spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG_NAME}")
spark.sql(f"USE CATALOG {CATALOG_NAME}")

# Crear schemas para arquitectura medallion
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {BRONZE_SCHEMA} COMMENT 'Raw data layer'")
spark.sql(
    f"CREATE SCHEMA IF NOT EXISTS {SILVER_SCHEMA} COMMENT 'Cleaned and transformed data'"
)
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {GOLD_SCHEMA} COMMENT 'Aggregated data for ML'")

print(f"✅ Catálogo '{CATALOG_NAME}' y schemas creados exitosamente")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Crear datos de ejemplo: Dataset de Churn de Clientes
# MAGIC
# MAGIC Dataset sintético para predecir abandono de clientes (caso de uso común en MLOps).

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType,
    DateType,
    BooleanType,
    TimestampType,
)
import random
from datetime import datetime, timedelta

# Seed para reproducibilidad
random.seed(42)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2.1 Bronze Layer: Datos crudos de clientes

# COMMAND ----------

# Generar datos de clientes
n_customers = 10000

customer_data = []
for i in range(n_customers):
    customer_id = f"CUST_{i:06d}"
    signup_date = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1460))

    # Características del cliente
    age = random.randint(18, 75)
    gender = random.choice(["M", "F", "O"])
    region = random.choice(["Lima", "Arequipa", "Cusco", "Trujillo", "Piura"])
    plan_type = random.choice(["Basic", "Standard", "Premium"])
    monthly_charges = round(random.uniform(29.99, 199.99), 2)
    total_charges = round(monthly_charges * random.randint(1, 48), 2)
    tenure_months = random.randint(1, 72)
    num_support_tickets = random.randint(0, 15)
    num_logins_last_month = random.randint(0, 30)

    # Variable objetivo (churn) - correlacionada con algunas features
    churn_prob = 0.15  # base probability
    if num_support_tickets > 5:
        churn_prob += 0.2
    if tenure_months < 6:
        churn_prob += 0.15
    if num_logins_last_month < 5:
        churn_prob += 0.1
    if plan_type == "Basic":
        churn_prob += 0.05

    churned = 1 if random.random() < churn_prob else 0

    customer_data.append(
        {
            "customer_id": customer_id,
            "signup_date": signup_date,
            "age": age,
            "gender": gender,
            "region": region,
            "plan_type": plan_type,
            "monthly_charges": monthly_charges,
            "total_charges": total_charges,
            "tenure_months": tenure_months,
            "num_support_tickets": num_support_tickets,
            "num_logins_last_month": num_logins_last_month,
            "churned": churned,
            "ingestion_timestamp": datetime.now(),
        }
    )

# Crear DataFrame
customers_df = spark.createDataFrame(customer_data)

# Escribir a Bronze
customers_df.write.mode("overwrite").saveAsTable(
    f"{CATALOG_NAME}.{BRONZE_SCHEMA}.customers_raw"
)

print(f"✅ Tabla bronze.customers_raw creada con {n_customers} registros")
display(customers_df.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2.2 Bronze Layer: Datos de transacciones

# COMMAND ----------

# Generar transacciones para cada cliente
transactions_data = []
for customer in customer_data[:5000]:  # Solo primeros 5000 para demo
    num_transactions = random.randint(1, 50)
    for _ in range(num_transactions):
        txn_date = customer["signup_date"] + timedelta(days=random.randint(0, 365))
        transactions_data.append(
            {
                "transaction_id": f"TXN_{len(transactions_data):08d}",
                "customer_id": customer["customer_id"],
                "transaction_date": txn_date,
                "amount": round(random.uniform(10.0, 500.0), 2),
                "category": random.choice(
                    ["Subscription", "Add-on", "Upgrade", "Refund"]
                ),
                "payment_method": random.choice(
                    ["Credit Card", "Debit Card", "Bank Transfer", "Digital Wallet"]
                ),
                "status": random.choices(
                    ["Completed", "Pending", "Failed"], weights=[0.9, 0.07, 0.03]
                )[0],
            }
        )

transactions_df = spark.createDataFrame(transactions_data)
transactions_df.write.mode("overwrite").saveAsTable(
    f"{CATALOG_NAME}.{BRONZE_SCHEMA}.transactions_raw"
)

print(f"✅ Tabla bronze.transactions_raw creada con {len(transactions_data)} registros")
display(transactions_df.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2.3 Silver Layer: Datos limpios y transformados

# COMMAND ----------

# Leer de bronze y limpiar
customers_silver = (
    spark.table(f"{CATALOG_NAME}.{BRONZE_SCHEMA}.customers_raw")
    .withColumn(
        "age_group",
        F.when(F.col("age") < 25, "18-24")
        .when(F.col("age") < 35, "25-34")
        .when(F.col("age") < 45, "35-44")
        .when(F.col("age") < 55, "45-54")
        .otherwise("55+"),
    )
    .withColumn(
        "is_high_value", F.when(F.col("monthly_charges") > 100, True).otherwise(False)
    )
    .withColumn("processing_timestamp", F.current_timestamp())
)

customers_silver.write.mode("overwrite").saveAsTable(
    f"{CATALOG_NAME}.{SILVER_SCHEMA}.customers_cleaned"
)

print(f"✅ Tabla silver.customers_cleaned creada")
display(customers_silver.limit(5))

# COMMAND ----------

# Agregar transacciones por cliente
transactions_agg = (
    spark.table(f"{CATALOG_NAME}.{BRONZE_SCHEMA}.transactions_raw")
    .groupBy("customer_id")
    .agg(
        F.count("*").alias("total_transactions"),
        F.sum("amount").alias("total_spent"),
        F.avg("amount").alias("avg_transaction_amount"),
        F.max("transaction_date").alias("last_transaction_date"),
        F.sum(F.when(F.col("status") == "Failed", 1).otherwise(0)).alias(
            "failed_transactions"
        ),
    )
)

transactions_agg.write.mode("overwrite").saveAsTable(
    f"{CATALOG_NAME}.{SILVER_SCHEMA}.transactions_aggregated"
)

print(f"✅ Tabla silver.transactions_aggregated creada")
display(transactions_agg.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2.4 Gold Layer: Feature Store para ML

# COMMAND ----------

# Crear feature table para modelo de churn
features_df = (
    spark.table(f"{CATALOG_NAME}.{SILVER_SCHEMA}.customers_cleaned")
    .join(
        spark.table(f"{CATALOG_NAME}.{SILVER_SCHEMA}.transactions_aggregated"),
        on="customer_id",
        how="left",
    )
    .select(
        "customer_id",
        "age",
        "age_group",
        "tenure_months",
        "monthly_charges",
        "total_charges",
        "num_support_tickets",
        "num_logins_last_month",
        "is_high_value",
        "plan_type",
        "region",
        F.coalesce("total_transactions", F.lit(0)).alias("total_transactions"),
        F.coalesce("total_spent", F.lit(0.0)).alias("total_spent"),
        F.coalesce("avg_transaction_amount", F.lit(0.0)).alias(
            "avg_transaction_amount"
        ),
        F.coalesce("failed_transactions", F.lit(0)).alias("failed_transactions"),
        "churned",
        F.current_timestamp().alias("feature_timestamp"),
    )
)

features_df.write.mode("overwrite").saveAsTable(
    f"{CATALOG_NAME}.{GOLD_SCHEMA}.churn_features"
)

print(f"✅ Tabla gold.churn_features creada (Feature Store)")
display(features_df.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Crear tabla de inferencia (para predicciones)

# COMMAND ----------

# Tabla para almacenar predicciones
inference_schema = StructType(
    [
        StructField("prediction_id", StringType(), False),
        StructField("customer_id", StringType(), False),
        StructField("prediction_date", TimestampType(), False),
        StructField("churn_probability", DoubleType(), True),
        StructField("predicted_churn", IntegerType(), True),
        StructField("model_version", StringType(), True),
        StructField("campaign_id", StringType(), True),
    ]
)

empty_inference_df = spark.createDataFrame([], inference_schema)
empty_inference_df.write.mode("overwrite").saveAsTable(
    f"{CATALOG_NAME}.{GOLD_SCHEMA}.churn_predictions"
)

print(f"✅ Tabla gold.churn_predictions creada (vacía, lista para inferencia)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Resumen de tablas creadas

# COMMAND ----------

print("=" * 60)
print("RESUMEN DE UNITY CATALOG SETUP")
print("=" * 60)
print(f"\n📁 Catálogo: {CATALOG_NAME}")
print("\n📊 Tablas creadas:")
print(f"\n  🥉 BRONZE (datos crudos):")
print(f"     - {CATALOG_NAME}.{BRONZE_SCHEMA}.customers_raw")
print(f"     - {CATALOG_NAME}.{BRONZE_SCHEMA}.transactions_raw")
print(f"\n  🥈 SILVER (datos limpios):")
print(f"     - {CATALOG_NAME}.{SILVER_SCHEMA}.customers_cleaned")
print(f"     - {CATALOG_NAME}.{SILVER_SCHEMA}.transactions_aggregated")
print(f"\n  🥇 GOLD (ML-ready):")
print(f"     - {CATALOG_NAME}.{GOLD_SCHEMA}.churn_features")
print(f"     - {CATALOG_NAME}.{GOLD_SCHEMA}.churn_predictions")
print("\n" + "=" * 60)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Verificar tablas creadas

# COMMAND ----------

# Listar todas las tablas del catálogo
display(spark.sql(f"SHOW TABLES IN {CATALOG_NAME}.{BRONZE_SCHEMA}"))
display(spark.sql(f"SHOW TABLES IN {CATALOG_NAME}.{SILVER_SCHEMA}"))
display(spark.sql(f"SHOW TABLES IN {CATALOG_NAME}.{GOLD_SCHEMA}"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Próximos pasos
# MAGIC
# MAGIC 1. Ejecutar los pipelines de campaña usando los datos creados
# MAGIC 2. Registrar modelos en Unity Catalog Model Registry
# MAGIC 3. Configurar Feature Store si está disponible
# MAGIC 4. Configurar lineage y gobernanza
