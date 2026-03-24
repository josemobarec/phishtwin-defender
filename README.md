# PhishTwin Defender

Plataforma defensiva de ciberseguridad orientada a detectar phishing moderno y BEC asistido por IA, y a generar simulaciones sintéticas seguras para entrenamiento interno.

## Qué resuelve

Las campañas de phishing actuales ya no dependen solo de enlaces evidentes o malware. Hoy combinan:
- BEC sin adjuntos ni URLs
- correos mejor redactados con IA
- QR phishing
- abuso de branding visual
- presión psicológica y urgencia contextual

PhishTwin Defender responde a ese problema con un pipeline híbrido de análisis:
- parsing de correos (`.eml` o JSON)
- extracción de señales técnicas, semánticas y visuales
- scoring de riesgo
- explicabilidad para analistas
- módulo seguro de generación sintética (`Twin Trainer`)
 
## Arquitectura

```text
[Web Dashboard] ---> [FastAPI API] ---> [Parser Service]
                             |         ---> [Risk Scoring Service]
                             |         ---> [Explainability Service]
                             |         ---> [Vision Service]
                             |         ---> [Synthetic Trainer]
                             |
                             +------> [PostgreSQL]
                             +------> [Redis (opcional para async)]
```

## Features del MVP

- Ingesta de emails en `.eml` o JSON
- Extracción de headers, texto, HTML, enlaces y metadatos
- Detección híbrida basada en reglas + scoring estructurado
- Risk score y veredicto (`benign`, `suspicious`, `malicious`)
- Resumen explicable para analistas
- Persistencia en PostgreSQL
- Auditoría de acciones
- Endpoint para análisis visual básico
- `Twin Trainer` para generar muestras sintéticas seguras

## Stack

- **Backend:** FastAPI + SQLModel
- **DB:** PostgreSQL
- **Cache/cola:** Redis
- **Parsing:** librerías estándar de email + BeautifulSoup
- **Infra local:** Docker Compose
- **Futuras extensiones:** XGBoost, sentence embeddings, visual embeddings, OpenTelemetry

## Cómo correrlo localmente

### 1. Clonar y configurar entorno

```bash
cp .env.example .env
```

### 2. Levantar servicios

```bash
docker compose up --build
```

La API quedará disponible en:
- `http://localhost:8000/docs`
- `http://localhost:8000/api/v1/health`

### 3. Probar análisis de demo

```bash
curl -X POST http://localhost:8000/api/v1/analyze-email \
  -H "Content-Type: application/json" \
  -d @datasets/demo/sample_invoice_bec.json
```

## Estructura del repo

```text
/apps
  /api                # FastAPI backend
  /web                # Placeholder del dashboard
/packages
  /common             # Tipos compartidos y utilidades futuras
/infra                # SQL schema y despliegue local
/datasets
  /demo               # Muestras seguras para demo
/docs                 # Arquitectura, ADRs, threat model
```

## Seguridad y límites éticos

Este proyecto es **exclusivamente defensivo y educativo**.

No incluye:
- envío de phishing real
- bypass de filtros
- robo de credenciales
- campañas ofensivas
- payloads maliciosos

`Twin Trainer` genera contenido sintético e inofensivo usando dominios no reales y artefactos pedagógicos.

## Próximas mejoras

- embeddings para similitud con correos legítimos históricos
- modelo tabular entrenado con features estructuradas
- modelo NLP para BEC sin enlaces
- análisis visual con embeddings y OCR opcional en sandbox
- RBAC completo y autenticación JWT
- observabilidad con OpenTelemetry + Prometheus
- dashboard en Next.js


