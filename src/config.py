# src/config.py

# GCP Settings
PROJECT_ID = "tu-proyecto-gcp"
REGION = "us-central1"

# Cloud Storage Paths
BRONZE_PATH = "gs://TU-BUCKET/bronze/vuelos_operacionales.csv"
SILVER_PATH = "gs://TU-BUCKET/silver/vuelos/"

# BigQuery Tables
GOLD_TABLE_KPIS = f"{PROJECT_ID}.dataset_vuelos.kpis_operacionales"