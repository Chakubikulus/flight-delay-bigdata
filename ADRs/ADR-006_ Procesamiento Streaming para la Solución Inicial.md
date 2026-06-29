## ADR-006: Procesamiento Streaming para la Solución Inicial

**Estado:** Descartado

### Contexto
Durante el diseño de la arquitectura se evaluó incorporar procesamiento en tiempo real mediante un enfoque Streaming, considerando servicios como Pub/Sub, Dataflow o una arquitectura Lambda/Kappa. Esta alternativa podía ser útil si el sistema necesitara reaccionar inmediatamente ante eventos operacionales, como retrasos en curso, cancelaciones en tiempo real o alertas instantáneas para equipos de operación.

Sin embargo, el objetivo principal del proyecto es apoyar decisiones estratégicas y analíticas sobre rentabilidad de rutas, comportamiento histórico de retrasos, patrones estacionales y evaluación de riesgos financieros. Estas decisiones no requieren procesamiento segundo a segundo, sino análisis batch diario y agregaciones mensuales.

### Decisión
Se descarta implementar procesamiento Streaming en la versión actual del proyecto y se mantiene una arquitectura Batch sobre Cloud Storage, Dataproc y BigQuery.

El procesamiento se ejecutará mediante cargas programadas, permitiendo consolidar información histórica y generar métricas analíticas para consumo posterior en dashboards y modelos predictivos.

### Alternativas Consideradas
- **Alternativa 1: Streaming con Pub/Sub + Dataflow.**
  - Ventajas: procesamiento casi en tiempo real, capacidad de emitir alertas inmediatas, mejor soporte para eventos operacionales críticos.
  - Desventajas: mayor complejidad arquitectónica, mayor costo operativo, requiere infraestructura activa de forma continua, no responde directamente al objetivo principal del proyecto.

- **Alternativa 2: Arquitectura Lambda.**
  - Ventajas: combina procesamiento batch y streaming, permite análisis histórico y eventos recientes.
  - Desventajas: duplica lógica de procesamiento, aumenta costos de desarrollo y mantenimiento, requiere mayor madurez operacional del equipo.

### Alternativa elegida
**Se eligió mantener una arquitectura Batch para la solución inicial y descartar Streaming en esta etapa del proyecto.**

### Consecuencias
- Menor complejidad inicial.
- Reducción de costos operacionales.
- Mayor alineación con el caso de uso estratégico y estacional.
- Facilidad de operación para un equipo de ingeniería reducido.
- Mejor control del pipeline mediante ejecuciones programadas.
- La plataforma no entrega alertas en tiempo real.
- No permite reaccionar inmediatamente ante eventos operacionales durante el día.
- Si el negocio requiere monitoreo operacional en vivo, será necesario rediseñar la arquitectura.
