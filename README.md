# flight-delay-bigdata

Plataforma analítica para predicción de retrasos aéreos y evaluación de rentabilidad de rutas, basada en datos históricos del BTS (Bureau of Transportation Statistics). 
Proyecto integrador del Magíster en Data Science, Universidad del Desarrollo 2026.

**Integrantes:** María Vásquez Tapia · Camila Figueroa Muñoz · Diego Morales Valenzuela

---

## Sobre el proyecto

La industria aérea genera millones de registros diarios de vuelos, retrasos y cancelaciones. Este pipeline Lakehouse procesa más de 26 millones de registros históricos (2022–2025) para identificar rutas con alto riesgo financiero y predecir retrasos sistémicos causados por clima o congestión aérea. El objetivo final es proveer a los equipos de operaciones y gerencia una herramienta para tomar decisiones estratégicas fundamentadas en datos.

---

## Arquitectura (Medallion)

El pipeline implementa un enfoque Lakehouse desacoplando el almacenamiento del cómputo sobre Google Cloud Platform (GCP):

```text
BTS / Kaggle CSV
      |
   Bronze  →  Cloud Storage (Datos crudos inmutables, CSV)
      |
   Silver  →  Cloud Storage (Datos limpios y curados, Apache Parquet, particionado por YEAR/MONTH, PII hasheada)
      |
    Gold   →  BigQuery (Tablas analíticas agregadas, KPIs operacionales y métricas de riesgo)
      |
   Looker Studio / Jupyter Notebooks (Consumo Analítico)
```

## Stack Tecnológico Final: 
Cloud Storage (Data Lake), Cloud Dataproc con PySpark (Motor de procesamiento), BigQuery (Data Warehouse), Cloud Scheduler + Cloud Functions (Orquestación Batch), Looker Studio (BI).

---

## Instrucciones de Instalación y Ejecución

# Entorno de Desarrollo Limitado (Google Colab / Sin credenciales GCP)
Para pruebas rápidas de la lógica de transformación:

- Abre el notebook ubicado en notebooks/demo_pipeline_vuelos_produccion.ipynb.

- Ejecuta todas las celdas secuencialmente.
Nota: Si no hay conexión a GCP, el pipeline generará automáticamente datos sintéticos con el mismo esquema del dataset real BTS para demostrar el flujo.

# Entorno de Producción (GCP)
1. Clonar el repositorio y configurar credenciales locales:
Bash: `gcloud auth application-default login`
2. Instalar dependencias requeridas:
Bash: `pip install pyspark==4.0.2`
3. En la celda bronze-code del notebook/script principal, actualizar la URI apuntando a tu bucket de Cloud Storage:
   ```python
   uri_bronze = "gs://TU-BUCKET/bronze/vuelos_operacionales.csv"
   ```
Lanzar la ejecución del pipeline.
---
## Manual de Operación Final
La plataforma está diseñada para operar bajo un modelo Batch Diario automatizado y basado en principios FinOps.

- Orquestación: El flujo es gatillado diariamente mediante Cloud Scheduler, el cual invoca una Cloud Function.

- Gestión de Infraestructura (Clústeres Efímeros): La Cloud Function despliega un clúster de Dataproc on-demand. Una vez que el job de PySpark finaliza la ingesta (Bronze -> Silver) y la carga (Silver -> Gold), el clúster se destruye automáticamente para evitar costos de inactividad 24/7.

- Monitoreo y Observabilidad: Los logs de ejecución, alertas operacionales y métricas del pipeline deben ser monitoreados a través de Cloud Logging.

- Gestión de Fallos: En caso de caída del pipeline, la inmutabilidad de la capa Bronze permite reprocesar la carga del día sin afectar el histórico, volviendo a ejecutar el job de Dataproc para esa partición específica de fecha.

---
## Datos de entrada y salida

| Capa | Formato | Descripción |
|------|---------|-------------|
| Bronze | CSV (GCS) | Registros crudos originales de la BTS. Contiene fechas, aeropuertos, aerolíneas y causas de retraso (ej. Weather Delay, NASDelay). |
| Silver | Apache Parquet (GCS) | Datos limpios y normalizados. Particionados físicamente por YEAR y MONTH para optimizar consultas I/O. Datos sensibles de pasajeros (PII) ofuscados con Hashing SHA-256. |
| Gold | Tablas Nativas (BigQuery) | Estructuras altamente agregadas listas para consumo. Incluye: Atraso promedio, % de cancelación, percentiles (p90) y KPIs financieros/operacionales por ruta y temporada.|

---

## Gobierno, Seguridad y Optimizaciones

- Seguridad y Privacidad: Control de acceso mediante políticas Least Privilege de IAM. Enmascaramiento de PII mediante Hashing criptográfico (SHA-256) aplicado en la capa Silver.

- Optimización de Cómputo (Spark): Uso de Broadcast Joins para eliminar cuellos de botella de red (aceleración medida del 64.6%), implementación de .cache() estratégico y activación de Adaptive Query Execution (AQE).

- Estrategia FinOps: La migración a formatos columnares (Parquet), particionamiento de datos, rightsizing de la orquestación (reemplazo de Composer por Scheduler+Functions) y el uso de clústeres efímeros lograron reducir el TCO proyectado en un 66% (reduciendo de $116.05 USD a $39.53 USD mensuales).

---

## Estructura del repositorio

```
flight-delay-bigdata/
├── README.md
├── notebooks/
│   └── demo_pipeline_vuelos_produccion.ipynb
└── docs/
    └── Fase-3-Informe-Tecnico.docx
```
---

## Declaración de uso de IA

Se usaron Gemini y ChatGPT para estructurar partes de la propuesta, refinar redacción y co-diseñar el esquema de arquitectura. El contenido fue revisado y es responsabilidad del equipo.
