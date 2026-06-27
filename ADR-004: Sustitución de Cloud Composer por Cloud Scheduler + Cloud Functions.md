ADR-004: Sustitución de Cloud Composer por Cloud Scheduler + Cloud Functions

Estado: Aceptado
Contexto

La arquitectura inicial consideraba utilizar Cloud Composer para la orquestación de pipelines. Sin embargo, el flujo implementado consiste en un único proceso Batch diario con lógica relativamente simple. El análisis de costos mostró que Composer introducía una complejidad y un costo operativo desproporcionados respecto de los requerimientos reales del proyecto.
Decisión

Reemplazar Cloud Composer por una combinación de Cloud Scheduler y Cloud Functions para la ejecución y control de los pipelines.
Alternativas Consideradas

    Alternativa 1: Mantener Cloud Composer.
        Ventajas: gestión avanzada de DAGs, escalabilidad para flujos complejos.
        Desventajas: mayor costo mensual, sobreingeniería para el caso de uso actual.

    Alternativa 2: Ejecución Manual.
        Ventajas: sin costo adicional.
        Desventajas: dependencia operativa, riesgo de errores humanos.

Alternativa elegida

Se eligió Cloud Scheduler + Cloud Functions como mecanismo de orquestación.
Consecuencias

    Reducción aproximada del 56% en costos de orquestación.
    Menor complejidad arquitectónica.
    Menor esfuerzo de administración.
    Menor flexibilidad para futuros pipelines complejos.
    Necesidad de rediseño si la plataforma crece significativamente.
