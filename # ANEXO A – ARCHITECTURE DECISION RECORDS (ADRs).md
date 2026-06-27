# ANEXO A – ARCHITECTURE DECISION RECORDS (ADRs)

## ADR-001: Adopción de Arquitectura Lakehouse con Patrón Medallion

**Estado:** Aceptado

### Contexto
El proyecto requiere procesar más de 26 millones de registros históricos de vuelos provenientes de la Bureau of Transportation Statistics (BTS). La solución debe soportar almacenamiento masivo, procesamiento distribuido y consumo analítico, manteniendo costos controlados y permitiendo futuras capacidades de Machine Learning. Durante el diseño inicial se evaluó utilizar una arquitectura basada exclusivamente en Data Warehouse o, alternativamente, un Data Lake tradicional.

### Decisión
Se adopta una arquitectura Lakehouse basada en el patrón Medallion, compuesta por las capas Bronze, Silver y Gold.

- **Bronze:** almacenamiento de datos crudos.
- **Silver:** transformación y curación de datos.
- **Gold:** consumo analítico y explotación.

### Alternativas Consideradas
- **Alternativa 1: Data Warehouse Tradicional.**
  - Ventajas: simplicidad conceptual, facilidad para consultas SQL.
  - Desventajas: mayor costo de almacenamiento, menor flexibilidad para futuros modelos ML, dependencia de estructuras rígidas.

- **Alternativa 2: Data Lake Puro.**
  - Ventajas: bajo costo, alta flexibilidad.
  - Desventajas: mayor complejidad de gobierno, dificultad para consumo analítico directo.

### Alternativa elegida
**Se eligió la arquitectura Lakehouse con patrón Medallion (Bronze/Silver/Gold).** 

### Consecuencias
- Separación clara de responsabilidades.
- Escalabilidad horizontal.
- Compatibilidad con analítica y Machine Learning.
- Mejor gobernanza de datos.
- Mayor complejidad inicial.
- Necesidad de administrar múltiples capas de datos.

***

## ADR-002: Uso de Apache Parquet como Formato de Persistencia en Silver

**Estado:** Aceptado

### Contexto
Los archivos originales BTS son distribuidos en formato CSV. Durante las pruebas iniciales se observó que el procesamiento sobre CSV genera lecturas completas de archivos, incrementando tiempos de ejecución y costos de procesamiento. La plataforma requiere optimizar consultas analíticas sobre un volumen superior a 26 millones de registros.

### Decisión
Persistir la capa Silver utilizando Apache Parquet comprimido mediante Snappy.

### Alternativas Consideradas
- **Alternativa 1: Mantener CSV.**
  - Ventajas: simplicidad, compatibilidad universal.
  - Desventajas: lectura completa de archivos, mayor consumo de almacenamiento, menor rendimiento.

- **Alternativa 2: JSON.**
  - Ventajas: flexibilidad estructural.
  - Desventajas: mayor tamaño de almacenamiento, rendimiento inferior para analítica.

### Alternativa elegida
**Se eligió Apache Parquet comprimido con Snappy para la capa Silver.** 

### Consecuencias
- Reducción del volumen almacenado.
- Lectura selectiva por columnas.
- Mejor rendimiento de Spark.
- Menor costo de procesamiento.
- Mayor complejidad operacional.
- Dependencia de herramientas compatibles con Parquet.

***

## ADR-003: Implementación de Clústeres Efímeros Dataproc

**Estado:** Aceptado

### Contexto
El procesamiento de datos se realiza mediante ejecuciones Batch programadas diariamente. Durante el diseño de infraestructura surgió la decisión de mantener un clúster Dataproc permanente o aprovisionarlo bajo demanda. Mantener recursos activos continuamente genera costos incluso cuando no existen procesos ejecutándose.

### Decisión
Implementar clústeres efímeros que se crean al inicio de cada ejecución y se eliminan automáticamente una vez finalizado el procesamiento.

### Alternativas Consideradas
- **Alternativa 1: Clúster Permanente.**
  - Ventajas: menor tiempo de inicio, mayor simplicidad operacional.
  - Desventajas: costos permanentes, recursos ociosos gran parte del tiempo.

- **Alternativa 2: Serverless Spark.**
  - Ventajas: menor administración.
  - Desventajas: menor control de configuración, limitaciones de personalización.

### Alternativa elegida
**Se eligieron clústeres efímeros Dataproc.** 

### Consecuencias
- Reducción significativa de costos.
- Mejor alineación con principios FinOps.
- Escalabilidad bajo demanda.
- Tiempo adicional de aprovisionamiento.
- Dependencia de automatizaciones de creación y destrucción.

***

## ADR-004: Sustitución de Cloud Composer por Cloud Scheduler + Cloud Functions

**Estado:** Aceptado

### Contexto
La arquitectura inicial consideraba utilizar Cloud Composer para la orquestación de pipelines. Sin embargo, el flujo implementado consiste en un único proceso Batch diario con lógica relativamente simple. El análisis de costos mostró que Composer introducía una complejidad y un costo operativo desproporcionados respecto de los requerimientos reales del proyecto.

### Decisión
Reemplazar Cloud Composer por una combinación de Cloud Scheduler y Cloud Functions para la ejecución y control de los pipelines.

### Alternativas Consideradas
- **Alternativa 1: Mantener Cloud Composer.**
  - Ventajas: gestión avanzada de DAGs, escalabilidad para flujos complejos.
  - Desventajas: mayor costo mensual, sobreingeniería para el caso de uso actual.

- **Alternativa 2: Ejecución Manual.**
  - Ventajas: sin costo adicional.
  - Desventajas: dependencia operativa, riesgo de errores humanos.

### Alternativa elegida
**Se eligió Cloud Scheduler + Cloud Functions como mecanismo de orquestación.** 

### Consecuencias
- Reducción aproximada del 56% en costos de orquestación.
- Menor complejidad arquitectónica.
- Menor esfuerzo de administración.
- Menor flexibilidad para futuros pipelines complejos.
- Necesidad de rediseño si la plataforma crece significativamente.

***

## ADR-005: Estrategia de Borrado y Derecho al Olvido bajo GDPR y Ley 21.719

**Estado:** Aceptado

### Contexto
Durante la revisión arquitectónica de la Fase 3 se recibió un requerimiento urgente de borrado de datos de pasajeros bajo GDPR (Artículo 17, Derecho de Supresión) y la Ley 21.719 de Chile. La arquitectura Medallion almacena datos en tres capas independientes, y la capa Bronze es por diseño inmutable. La solicitud exige propagar la supresión a todas las capas donde el dato pueda estar presente.

### Decisión
Implementar una estrategia de borrado por capas :

- **Bronze:** reescritura del archivo CSV en Cloud Storage sin los registros afectados, o marcado en un deletion log.
- **Silver:** repartición y reescritura de los archivos Parquet afectados.
- **Gold:** DELETE o MERGE en BigQuery sobre tablas que contengan métricas derivadas del pasajero afectado.
- **Registro de supresiones:** mantener un log con timestamp, identificador anonimizado del solicitante y confirmación de ejecución en cada capa.

### Alternativas Consideradas
- **Alternativa 1: No borrar Bronze por ser inmutable por diseño.**
  - Preserva la integridad del historial, pero incumple GDPR Art. 17 y la Ley 21.719.

- **Alternativa 2: Crypto-Shredding.**
  - Técnicamente elegante, pero requiere cifrado individual desde el origen, no implementado actualmente.

- **Alternativa 3: Borrado lógico con tabla de supresiones.**
  - Menor impacto operacional, pero no garantiza supresión física ante una auditoría regulatoria.

### Alternativa elegida
**Se eligió una estrategia de borrado por capas con trazabilidad y registro de supresiones.** 

### Consecuencias
- Cumplimiento del derecho de supresión bajo GDPR Art. 17 y Ley 21.719.
- Trazabilidad completa del proceso.
- Reducción del riesgo legal y reputacional.
- La arquitectura queda preparada para atender solicitudes de forma operacional y repetible.
- La reescritura de archivos Parquet es costosa en I/O.
- La inmutabilidad de Bronze entra en tensión directa con el derecho de supresión.
- El borrado en BigQuery mediante DML puede generar costos adicionales.
