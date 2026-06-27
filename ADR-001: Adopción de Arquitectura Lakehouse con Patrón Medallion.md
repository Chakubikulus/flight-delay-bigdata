ADR-001: Adopción de Arquitectura Lakehouse con Patrón Medallion

Estado: Aceptado
Contexto

El proyecto requiere procesar más de 26 millones de registros históricos de vuelos provenientes de la Bureau of Transportation Statistics (BTS). La solución debe soportar almacenamiento masivo, procesamiento distribuido y consumo analítico, manteniendo costos controlados y permitiendo futuras capacidades de Machine Learning. Durante el diseño inicial se evaluó utilizar una arquitectura basada exclusivamente en Data Warehouse o, alternativamente, un Data Lake tradicional.
Decisión

Se adopta una arquitectura Lakehouse basada en el patrón Medallion, compuesta por las capas Bronze, Silver y Gold.

    Bronze: almacenamiento de datos crudos.
    Silver: transformación y curación de datos.
    Gold: consumo analítico y explotación.

Alternativas Consideradas

    Alternativa 1: Data Warehouse Tradicional.
        Ventajas: simplicidad conceptual, facilidad para consultas SQL.
        Desventajas: mayor costo de almacenamiento, menor flexibilidad para futuros modelos ML, dependencia de estructuras rígidas.

    Alternativa 2: Data Lake Puro.
        Ventajas: bajo costo, alta flexibilidad.
        Desventajas: mayor complejidad de gobierno, dificultad para consumo analítico directo.

Alternativa elegida

Se eligió la arquitectura Lakehouse con patrón Medallion (Bronze/Silver/Gold).
Consecuencias

    Separación clara de responsabilidades.
    Escalabilidad horizontal.
    Compatibilidad con analítica y Machine Learning.
    Mejor gobernanza de datos.
    Mayor complejidad inicial.
    Necesidad de administrar múltiples capas de datos.
