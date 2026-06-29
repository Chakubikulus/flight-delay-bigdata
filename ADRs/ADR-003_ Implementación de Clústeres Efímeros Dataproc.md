ADR-003: Implementación de Clústeres Efímeros Dataproc

Estado: Aceptado
Contexto

El procesamiento de datos se realiza mediante ejecuciones Batch programadas diariamente. Durante el diseño de infraestructura surgió la decisión de mantener un clúster Dataproc permanente o aprovisionarlo bajo demanda. Mantener recursos activos continuamente genera costos incluso cuando no existen procesos ejecutándose.
Decisión

Implementar clústeres efímeros que se crean al inicio de cada ejecución y se eliminan automáticamente una vez finalizado el procesamiento.
Alternativas Consideradas

    Alternativa 1: Clúster Permanente.
        Ventajas: menor tiempo de inicio, mayor simplicidad operacional.
        Desventajas: costos permanentes, recursos ociosos gran parte del tiempo.

    Alternativa 2: Serverless Spark.
        Ventajas: menor administración.
        Desventajas: menor control de configuración, limitaciones de personalización.

Alternativa elegida

Se eligieron clústeres efímeros Dataproc.
Consecuencias

    Reducción significativa de costos.
    Mejor alineación con principios FinOps.
    Escalabilidad bajo demanda.
    Tiempo adicional de aprovisionamiento.
    Dependencia de automatizaciones de creación y destrucción.
