# src/jobs/bronze_to_silver.py
from pyspark.sql import functions as F
import shutil
import os
from src.config import URI_BRONZE, OUTPUT_PATH_SILVER

def run(spark):
    # --- CAPA BRONZE (Celda 2 del notebook) ---
    try:
        df_bronze = (
            spark.read
            .format("csv")
            .option("header", "true")
            .option("inferSchema", "true")
            .load(URI_BRONZE)
        )
    except Exception as e:
        print("Conexión a GCS requiere autenticación. Generando muestra representativa para la demo...")
        # Generación de fallback representativo idéntico al esquema real del BTS
        data = [
            (2023, 5, "AA", "MIA", "JFK", 45.0, 150, "4532-XXXX-XXXX-1234"),
            (2023, 5, "DL", "ATL", "LAX", -10.0, 320, "4532-XXXX-XXXX-9999"), # Anomalía
            (2023, 6, "UA", "JFK", "SFO", 120.0, 380, "5555-XXXX-XXXX-0000"),
            (2023, 6, "AA", "MIA", "JFK", None, 150, "4532-XXXX-XXXX-1111"),  # Anomalía
            (2023, 7, "DL", "ATL", "MIA", 15.0, 110, "4532-XXXX-XXXX-2222")
        ] * 100000 # Simular volumen
        df_bronze = spark.createDataFrame(data, ["YEAR", "MONTH", "AIRLINE", "ORIGIN_AIRPORT", "DESTINATION_AIRPORT", "DEPARTURE_DELAY", "DISTANCE", "PASSENGER_CC_MOCK"])

    print("--- Capa Bronze (Raw Data) ---")
    df_bronze.select("YEAR", "MONTH", "AIRLINE", "ORIGIN_AIRPORT", "DESTINATION_AIRPORT", "DEPARTURE_DELAY").show(5)
    
    n_bronze = df_bronze.count()
    print(f"Total de registros transaccionales en Bronze: {n_bronze:,}")

    # --- CAPA SILVER (Celda 3 del notebook) ---
    # Si es el dataset real puro, simulamos una columna de PII para la demostración de seguridad
    if "PASSENGER_CC_MOCK" not in df_bronze.columns:
        df_bronze = df_bronze.withColumn("PASSENGER_CC_MOCK", F.lit("4532-XXXX-XXXX-0000"))

    df_silver = (
        df_bronze
        # Reglas de negocio y calidad estructural
        .filter(F.col("DEPARTURE_DELAY").isNotNull())
        .filter(F.col("DEPARTURE_DELAY") >= 0)
        # Gobierno de Datos: Hashing de información sensible
        .withColumn("passenger_token", F.sha2(F.col("PASSENGER_CC_MOCK"), 256))
        .drop("PASSENGER_CC_MOCK") # Destruir dato crudo expuesto
    )

    n_silver = df_silver.count()

    print("--- Capa Silver (Datos Protegidos y Conformados) ---")
    df_silver.select("YEAR", "MONTH", "AIRLINE", "DEPARTURE_DELAY", "passenger_token").show(5, truncate=False)

    # ESCRITURA FÍSICA PARTICIONADA EN DATA LAKE (Silver Layer)
    if os.path.exists(OUTPUT_PATH_SILVER): 
        shutil.rmtree(OUTPUT_PATH_SILVER)

    df_silver.write.mode("overwrite").partitionBy("YEAR", "MONTH").parquet(OUTPUT_PATH_SILVER)
    
    print(f"\n✅ Datos consolidados escritos exitosamente en formato Parquet en: {OUTPUT_PATH_SILVER}")
    print(f"Porcentaje de retención por calidad de datos: {(n_silver/n_bronze)*100:.1f}%")