# src/utils.py
from pyspark.sql import SparkSession

def get_spark_session():
    # Inicialización con optimizaciones de Spark activas (AQE) exactamente como en el notebook
    spark = SparkSession.builder \
        .appName("FlightDelays_Rubric_Compliant_RealData") \
        .config("spark.sql.shuffle.partitions", "8") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    return spark