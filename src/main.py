# src/main.py
import sys
from utils import get_spark_session
from jobs import bronze_to_silver, silver_to_gold

def main():
    # Inicializar sesión Spark
    spark = get_spark_session()
    
    try:
        # Ejecutar Pipeline secuencialmente
        bronze_to_silver.run(spark)
        silver_to_gold.run(spark)
        
    except Exception as e:
        print(f"Error en la ejecución del pipeline: {e}")
        sys.exit(1)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()