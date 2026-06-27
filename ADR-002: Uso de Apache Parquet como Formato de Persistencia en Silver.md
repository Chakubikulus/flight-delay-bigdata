ADR-002: Uso de Apache Parquet como Formato de Persistencia en Silver

Estado: Aceptado
Contexto

Los archivos originales BTS son distribuidos en formato CSV. Durante las pruebas iniciales se observó que el procesamiento sobre CSV genera lecturas completas de archivos, incrementando tiempos de ejecución y costos de procesamiento. La plataforma requiere optimizar consultas analíticas sobre un volumen superior a 26 millones de registros.
Decisión

Persistir la capa Silver utilizando Apache Parquet comprimido mediante Snappy.
Alternativas Consideradas

    Alternativa 1: Mantener CSV.
        Ventajas: simplicidad, compatibilidad universal.
        Desventajas: lectura completa de archivos, mayor consumo de almacenamiento, menor rendimiento.

    Alternativa 2: JSON.
        Ventajas: flexibilidad estructural.
        Desventajas: mayor tamaño de almacenamiento, rendimiento inferior para analítica.

Alternativa elegida

Se eligió Apache Parquet comprimido con Snappy para la capa Silver.
Consecuencias

    Reducción del volumen almacenado.
    Lectura selectiva por columnas.
    Mejor rendimiento de Spark.
    Menor costo de procesamiento.
    Mayor complejidad operacional.
    Dependencia de herramientas compatibles con Parquet.
