# ANEXO A – ARCHITECTURE DECISION RECORDS (ADRs)

## ADR-001: Adopción de Arquitectura Lakehouse con Patrón Medallion

### Contexto
El proyecto requiere procesar más de 26 millones de registros históricos de vuelos provenientes de la Bureau of Transportation Statistics (BTS). La solución debe soportar almacenamiento masivo, procesamiento distribuido y consumo analítico, manteniendo costos controlados y permitiendo futuras capacidades de Machine Learning.

Durante el diseño inicial se evaluó utilizar una arquitectura basada exclusivamente en Data Warehouse o, alternativamente, un Data Lake tradicional.

### Decisión
Se adopta una arquitectura Lakehouse basada en el patrón Medallion, compuesta por las capas Bronze, Silver y Gold.

- **Bronze:** almacenamiento de datos crudos.
- **Silver:** transformación y curación de datos.
- **Gold:** consumo analítico y explotación.

### Alternativas Consideradas

#### Alternativa 1: Data Warehouse Tradicional
**Ventajas:**
- Simplicidad conceptual.
- Facilidad para consultas SQL.

**Desventajas:**
- Mayor costo de almacenamiento.
- Menor flexibilidad para futuros modelos ML.
- Dependencia de estructuras rígidas.

#### Alternativa 2: Data Lake Puro
**Ventajas:**
- Bajo costo.
- Alta flexibilidad.

**Desventajas:**
- Mayor complejidad de gobierno.
- Dificultad para consumo analítico directo.

### Consecuencias

#### Positivas
- Separación clara de responsabilidades.
- Escalabilidad horizontal.
- Compatibilidad con analítica y Machine Learning.
- Mejor gobernanza de datos.

#### Negativas
- Mayor complejidad inicial.
- Necesidad de administrar múltiples capas de datos.

---

## ADR-002: Uso de Apache Parquet como Formato de Persistencia en Silver

### Contexto
Los archivos originales BTS son distribuidos en formato CSV. Durante las pruebas iniciales se observó que el procesamiento sobre CSV genera lecturas completas de archivos, incrementando tiempos de ejecución y costos de procesamiento.

La plataforma requiere optimizar consultas analíticas sobre un volumen superior a 26 millones de registros.

### Decisión
Persistir la capa Silver utilizando Apache Parquet comprimido mediante Snappy.

### Alternativas Consideradas

#### Alternativa 1: Mantener CSV
**Ventajas:**
- Simplicidad.
- Compatibilidad universal.

**Desventajas:**
- Lectura completa de archivos.
- Mayor consumo de almacenamiento.
- Menor rendimiento.

#### Alternativa 2: JSON
**Ventajas:**
- Flexibilidad estructural.

**Desventajas:**
- Mayor tamaño de almacenamiento.
- Rendimiento inferior para analítica.

### Consecuencias

#### Positivas
- Reducción del volumen almacenado.
- Lectura selectiva por columnas.
- Mejor rendimiento de Spark.
- Menor costo de procesamiento.

#### Negativas
- Mayor complejidad operacional.
- Dependencia de herramientas compatibles con Parquet.

---

## ADR-003: Implementación de Clústeres Efímeros Dataproc

### Contexto
El procesamiento de datos se realiza mediante ejecuciones Batch programadas diariamente. Durante el diseño de infraestructura surgió la decisión de mantener un clúster Dataproc permanente o aprovisionarlo bajo demanda.

Mantener recursos activos continuamente genera costos incluso cuando no existen procesos ejecutándose.

### Decisión
Implementar clústeres efímeros que se crean al inicio de cada ejecución y se eliminan automáticamente una vez finalizado el procesamiento.

### Alternativas Consideradas

#### Alternativa 1: Clúster Permanente
**Ventajas:**
- Menor tiempo de inicio.
- Mayor simplicidad operacional.

**Desventajas:**
- Costos permanentes.
- Recursos ociosos gran parte del tiempo.

#### Alternativa 2: Serverless Spark
**Ventajas:**
- Menor administración.

**Desventajas:**
- Menor control de configuración.
- Limitaciones de personalización.

### Consecuencias

#### Positivas
- Reducción significativa de costos.
- Mejor alineación con principios FinOps.
- Escalabilidad bajo demanda.

#### Negativas
- Tiempo adicional de aprovisionamiento.
- Dependencia de automatizaciones de creación y destrucción.

---

## ADR-004: Sustitución de Cloud Composer por Cloud Scheduler + Cloud Functions

### Contexto
La arquitectura inicial consideraba utilizar Cloud Composer para la orquestación de pipelines. Sin embargo, el flujo implementado consiste en un único proceso Batch diario con lógica relativamente simple.

El análisis de costos mostró que Composer introducía una complejidad y un costo operativo desproporcionados respecto de los requerimientos reales del proyecto.

### Decisión
Reemplazar Cloud Composer por una combinación de Cloud Scheduler y Cloud Functions para la ejecución y control de los pipelines.

### Alternativas Consideradas

#### Alternativa 1: Mantener Cloud Composer
**Ventajas:**
- Gestión avanzada de DAGs.
- Escalabilidad para flujos complejos.

**Desventajas:**
- Mayor costo mensual.
- Sobreingeniería para el caso de uso actual.

#### Alternativa 2: Ejecución Manual
**Ventajas:**
- Sin costo adicional.

**Desventajas:**
- Dependencia operativa.
- Riesgo de errores humanos.

### Consecuencias

#### Positivas
- Reducción aproximada del 56% en costos de orquestación.
- Menor complejidad arquitectónica.
- Menor esfuerzo de administración.

#### Negativas
- Menor flexibilidad para futuros pipelines complejos.
- Necesidad de rediseño si la plataforma crece significativamente.

---

## ADR-005: Estrategia de Borrado y Derecho al Olvido bajo GDPR y Ley 21.719

### Contexto
Durante la revisión arquitectónica de la Fase 3 se recibió un requerimiento urgente de borrado de datos de pasajeros bajo GDPR (Artículo 17, Derecho de Supresión) y la Ley 21.719 de Chile, que regula la protección y tratamiento de datos personales y establece el derecho a la supresión como un derecho inalienable, ejercible de forma gratuita y sin dilación indebida.

El problema arquitectónico es concreto: la arquitectura Medallion almacena datos en tres capas independientes, y la capa Bronze es por diseño inmutable. El dato de pasajero en Silver fue hasheado con SHA-256, lo que impide su identificación directa, pero el registro original persiste en Bronze en CSV. Una solicitud de borrado exige propagar la supresión a través de todas las capas donde el dato pueda estar presente, dentro del plazo máximo de 30 días establecido por GDPR Art. 17.

### Decisión
Implementar una estrategia de borrado por capas:

- **Bronze:** reescritura del archivo CSV en Cloud Storage sin los registros afectados, o marcado en un deletion log que impida la repropagación del dato en futuros reprocesos.
- **Silver:** repartición y reescritura de los archivos Parquet afectados para eliminar la fila completa, dado que el hash SHA-256 no es reversible pero la fila persiste.
- **Gold:** DELETE o MERGE en BigQuery sobre tablas que contengan métricas derivadas del pasajero afectado.
- **Registro de supresiones:** mantener un log con timestamp, identificador anonimizado del solicitante y confirmación de ejecución en cada capa para efectos de auditoría regulatoria.

### Alternativas Consideradas

#### Alternativa 1: No borrar Bronze por ser inmutable por diseño
Preserva la integridad del historial, pero incumple directamente el GDPR Art. 17 y la Ley 21.719, que no admiten excepciones por criterios de diseño interno. Expone a la organización a sanciones regulatorias.

#### Alternativa 2: Crypto-Shredding
Destrucción de clave. Permite “borrar” sin reescribir archivos físicos destruyendo la clave Cloud KMS. Técnicamente elegante, pero requiere que el dato haya sido cifrado individualmente por pasajero desde el origen, lo que no está implementado en la arquitectura actual.

#### Alternativa 3: Borrado lógico con tabla de supresiones
Menor impacto operacional, pero el dato físico persiste en almacenamiento y puede no ser suficiente ante una auditoría regulatoria que exija demostrar la supresión física.

### Consecuencias

#### Positivas
- Cumplimiento del derecho de supresión bajo GDPR Art. 17 y Ley 21.719.
- Trazabilidad completa del proceso.
- Reducción del riesgo legal y reputacional.
- La arquitectura queda preparada para atender solicitudes de forma operacional y repetible.

#### Negativas
- La reescritura de archivos Parquet en Cloud Storage es costosa en I/O.
- La inmutabilidad de Bronze entra en tensión directa con el derecho de supresión.
- El borrado en BigQuery mediante DML puede generar costos adicionales.
