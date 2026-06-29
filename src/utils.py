# src/utils.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sha2

def get_spark_session(app_name="FlightDelayPipeline"):
    """Crea la sesión de Spark con optimizaciones habilitadas."""
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    return spark

def hash_pii_column(df, column_name):
    """Ofusca datos sensibles (PII) usando SHA-256."""
    return df.withColumn(column_name, sha2(col(column_name), 256))