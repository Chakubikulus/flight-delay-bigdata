# src/jobs/bronze_to_silver.py
from utils import hash_pii_column
from config import BRONZE_PATH, SILVER_PATH

def run(spark):
    print("Iniciando capa Bronze a Silver...")
    
    # 1. Leer CSV de Bronze
    df_bronze = spark.read.csv(BRONZE_PATH, header=True, inferSchema=True)
    
    # 2. Limpieza de datos y Hashing PII (Ej: ofuscar ID de pasajero o tripulación si existe)
    # df_clean = hash_pii_column(df_bronze, "passenger_id") 
    df_clean = df_bronze # Reemplazar con lógica real de limpieza
    
    # 3. Escritura particionada en formato Parquet en Silver
    (df_clean.write
     .mode("overwrite")
     .partitionBy("YEAR", "MONTH")
     .parquet(SILVER_PATH))
    
    print("Capa Silver actualizada exitosamente.")