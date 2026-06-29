# src/jobs/silver_to_gold.py
from pyspark.sql.functions import avg, count, broadcast, expr
from config import SILVER_PATH, GOLD_TABLE_KPIS

def run(spark):
    print("Iniciando capa Silver a Gold...")
    
    # 1. Leer Parquet desde Silver
    df_silver = spark.read.parquet(SILVER_PATH)
    
    # Usar .cache() si el dataframe se usará para múltiples tablas Gold
    df_silver.cache()
    
    # 2. Lógica de negocio (Ej: Atrasos promedios y % de cancelación por ruta)
    # Aquí puedes incluir tu optimización con "broadcast(df_dimension_aeropuertos)"
    
    df_gold = df_silver.groupBy("ORIGIN", "DEST").agg(
        avg("DEP_DELAY").alias("avg_delay"),
        (sum(expr("CAST(CANCELLED AS INT)")) / count("*") * 100).alias("cancellation_pct")
    )
    
    # 3. Escritura a BigQuery
    # Nota: Requiere tener configurado el conector de BQ en el clúster de Dataproc
    (df_gold.write
     .format("bigquery")
     .option("table", GOLD_TABLE_KPIS)
     .option("temporaryGcsBucket", "TU-BUCKET-TEMP-BQ")
     .mode("overwrite")
     .save())
     
    print("Capa Gold actualizada exitosamente en BigQuery.")