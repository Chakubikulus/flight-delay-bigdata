ADR-005: Estrategia de Borrado y Derecho al Olvido bajo GDPR y Ley 21.719

Estado: Aceptado
Contexto

Durante la revisión arquitectónica de la Fase 3 se recibió un requerimiento urgente de borrado de datos de pasajeros bajo GDPR (Artículo 17, Derecho de Supresión) y la Ley 21.719 de Chile. La arquitectura Medallion almacena datos en tres capas independientes, y la capa Bronze es por diseño inmutable. La solicitud exige propagar la supresión a todas las capas donde el dato pueda estar presente.
Decisión

Implementar una estrategia de borrado por capas :

    Bronze: reescritura del archivo CSV en Cloud Storage sin los registros afectados, o marcado en un deletion log.
    Silver: repartición y reescritura de los archivos Parquet afectados.
    Gold: DELETE o MERGE en BigQuery sobre tablas que contengan métricas derivadas del pasajero afectado.
    Registro de supresiones: mantener un log con timestamp, identificador anonimizado del solicitante y confirmación de ejecución en cada capa.

Alternativas Consideradas

    Alternativa 1: No borrar Bronze por ser inmutable por diseño.
        Preserva la integridad del historial, pero incumple GDPR Art. 17 y la Ley 21.719.

    Alternativa 2: Crypto-Shredding.
        Técnicamente elegante, pero requiere cifrado individual desde el origen, no implementado actualmente.

    Alternativa 3: Borrado lógico con tabla de supresiones.
        Menor impacto operacional, pero no garantiza supresión física ante una auditoría regulatoria.

Alternativa elegida

Se eligió una estrategia de borrado por capas con trazabilidad y registro de supresiones.
Consecuencias

    Cumplimiento del derecho de supresión bajo GDPR Art. 17 y Ley 21.719.
    Trazabilidad completa del proceso.
    Reducción del riesgo legal y reputacional.
    La arquitectura queda preparada para atender solicitudes de forma operacional y repetible.
    La reescritura de archivos Parquet es costosa en I/O.
    La inmutabilidad de Bronze entra en tensión directa con el derecho de supresión.
    El borrado en BigQuery mediante DML puede generar costos adicionales.
