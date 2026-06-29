# src/main.py
from src.utils import get_spark_session
from src.jobs import bronze_to_silver, silver_to_gold

def main():
    spark = get_spark_session()
    print(f"Motor PySpark inicializado. Versión: {spark.version}")
    
    try:
        # Ejecución Celda 2 y 3
        bronze_to_silver.run(spark)
        
        # Ejecución Celda 4 y 5
        silver_to_gold.run(spark)
        
    finally:
        # Cierre limpio (Celda 5)
        spark.stop()

if __name__ == "__main__":
    main()