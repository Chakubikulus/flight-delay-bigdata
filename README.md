# flight-delay-bigdata

Plataforma analítica para predicción de retrasos aéreos y evaluación de rentabilidad de rutas, basada en datos públicos del BTS (Bureau of Transportation Statistics). Proyecto integrador del Magíster en Data Science, Universidad del Desarrollo 2026.

**Integrantes:** María Vásquez Tapia · Camila Figueroa Muñoz · Diego Morales Valenzuela

---

## Sobre el proyecto

La industria aérea genera millones de registros diarios de vuelos, retrasos y cancelaciones. Este pipeline procesa 26 millones de registros históricos (2022–2025) para identificar rutas con alto riesgo financiero y predecir retrasos sistémicos causados por clima o congestión aérea. El objetivo final es darle a los equipos de operaciones de las aerolíneas una herramienta para tomar decisiones estratégicas sobre qué rutas mantener, ajustar o cancelar.

---

## Arquitectura

El pipeline sigue una arquitectura Medallion sobre GCP:

```
BTS / Kaggle CSV
      |
   Bronze  →  Cloud Storage (CSV crudo, inmutable)
      |
   Silver  →  Cloud Storage (Parquet, particionado por YEAR/MONTH, PII hasheada)
      |
    Gold   →  BigQuery (tablas agregadas para analítica)
      |
   Looker Studio / Colab
```

Servicios usados: Cloud Storage, Cloud Dataproc (PySpark), BigQuery, Cloud Composer (Airflow), Looker Studio.

---

## Cómo ejecutar

### Sin credenciales GCP (Google Colab)

Abre el notebook en `notebooks/demo_pipeline_vuelos_produccion.ipynb` y ejecuta todas las celdas. Si no hay conexión a GCP, el pipeline genera automáticamente datos sintéticos con el mismo esquema del dataset real, así que todo funciona igual.

### Con credenciales GCP

1. Autenticarse: `gcloud auth application-default login`
2. En la celda `bronze-code`, cambiar la URI del bucket:
   ```python
   uri_bronze = "gs://TU-BUCKET/bronze/vuelos_operacionales.csv"
   ```
3. Ejecutar el notebook completo.

**Requisito:**
```bash
pip install pyspark==4.0.2
```

---

## Estructura del repositorio

```
flight-delay-bigdata/
├── README.md
├── notebooks/
│   └── demo_pipeline_vuelos_produccion.ipynb
└── docs/
    └── Fase-2-Informe.docx
```

---

## Datos de entrada y salida

| Capa | Formato | Descripción |
|------|---------|-------------|
| Bronze | CSV | Registros crudos BTS — YEAR, MONTH, AIRLINE, ORIGIN, DEST, DEPARTURE_DELAY |
| Silver | Parquet particionado por YEAR/MONTH | Datos limpios, PII hasheada con SHA-256 |
| Gold | Tabla BigQuery | KPIs agregados por aerolínea, ruta y estacionalidad |

---

## Optimizaciones implementadas

- **Broadcast Join:** elimina el shuffle de red en los joins con tablas de dimensiones. Aceleración medida: 64.6%.
- **Caching:** `dfsilver.cache()` evita re-computar la capa Silver en cada acción downstream.
- **AQE activado:** `spark.sql.adaptive.enabled = true` para ajuste automático de particiones.
- **Clústeres efímeros en Dataproc:** se crean solo durante el job y se destruyen al terminar, reduciendo el costo mensual en un 66% respecto a mantener infraestructura activa 24/7.

---

## Gobierno y seguridad

- Los datos de pasajeros (PII) se hashean con SHA-256 en la capa Silver. El dato crudo se elimina del DataFrame antes de cualquier escritura.
- Control de acceso por roles IAM: los ingenieros de datos acceden a Bronze y Silver; los analistas de negocio tienen acceso solo a la capa Gold en BigQuery.
- Linaje documentado: BTS → Bronze (Cloud Storage) → Silver (Spark/Dataproc) → Gold (BigQuery).

---

## Estimación de costos mensuales (GCP)

| Escenario | Costo USD/mes |
|-----------|--------------|
| Baseline | $116.05 |
| + Rightsizing de orquestación | $51.20 |
| + Clústeres efímeros | $39.53 |

---

## Declaración de uso de IA

Se usaron Gemini y ChatGPT para estructurar partes de la propuesta, refinar redacción y co-diseñar el esquema de arquitectura. El contenido fue revisado y es responsabilidad del equipo.

