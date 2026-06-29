# src/jobs/silver_to_gold.py
from pyspark.sql import functions as F
import time
from src.config import OUTPUT_PATH_SILVER

def run(spark):
    # Leer el DataFrame guardado en Silver para simular el paso entre capas
    df_silver = spark.read.parquet(OUTPUT_PATH_SILVER)
    df_silver.cache()
    
    dim_airlines = spark.createDataFrame([
        ("AA", "American Airlines"),
        ("DL", "Delta Air Lines"),
        ("UA", "United Airlines"),
        ("WN", "Southwest Airlines")
    ], ["AIRLINE", "AIRLINE_NAME"])

    # --- ESCENARIO A: SIN OPTIMIZACIÓN (Join Estándar con Shuffle) ---
    t0 = time.time()
    df_gold_standard = df_silver.join(dim_airlines, "AIRLINE", "left") \
                                .groupBy("AIRLINE_NAME", "ORIGIN_AIRPORT", "DESTINATION_AIRPORT") \
                                .agg(F.avg("DEPARTURE_DELAY").alias("promedio_retraso_min"))
    df_gold_standard.collect() # Acción para gatillar el plan
    time_standard = time.time() - t0

    # --- ESCENARIO B: CON OPTIMIZACIÓN (Broadcast Join) ---
    t1 = time.time()
    df_gold_optimized = df_silver.join(F.broadcast(dim_airlines), "AIRLINE", "left") \
                                 .groupBy("AIRLINE_NAME", "ORIGIN_AIRPORT", "DESTINATION_AIRPORT") \
                                 .agg(F.avg("DEPARTURE_DELAY").alias("promedio_retraso_min"))
    df_gold_optimized.collect() # Acción para gatillar el plan
    time_optimized = time.time() - t1

    print("=" * 55)
    print(" MÉTRICAS DE OPTIMIZACIÓN DE RENDIMIENTO (FINOPS)")
    print("=" * 55)
    print(f" Tiempo ANTES (Join Pobre con Shuffle):   {time_standard:.4f} seg")
    print(f" Tiempo DESPUÉS (Uso de Broadcast Join):  {time_optimized:.4f} seg")
    # Manejo de división por cero en caso de que time_standard sea 0
    if time_standard > 0:
        print(f" Aceleración de procesamiento:            {((time_standard - time_optimized) / time_standard) * 100:.1f}%")

    # --- AUDITORÍA Y LIMPIEZA (Celda 5 del notebook) ---
    df_gold_optimized.explain(True)
    df_silver.unpersist()