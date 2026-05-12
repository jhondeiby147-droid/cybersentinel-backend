# CyberSentinel AI - Backend 🛡️

## Descripción
CyberSentinel AI es un sistema avanzado de análisis de vulnerabilidades de seguridad con un enfoque estricto en la privacidad y ejecución offline. Este repositorio contiene el código fuente del Backend, desarrollado en **Python** con **FastAPI**, diseñado para procesar texto, clasificar vulnerabilidades y extraer entidades técnicas críticas (NER) utilizando Deep Learning y expresiones regulares.

## Tecnologías Principales
- **Framework Web:** FastAPI (Python)
- **Motor de Deep Learning:** PyTorch / Hugging Face Transformers
- **Base de Datos:** PostgreSQL con ORM SQLAlchemy
- **Modelos IA:** - mDeBERTa-v3 (Zero-Shot Classification para Severidad)
  - Wikineural (Extracción de Entidades - NER)

## Arquitectura y Módulos Principales

### 1. Clasificación de Severidad (Zero-Shot)
Utiliza un pipeline basado en `mDeBERTa-v3` (`ai_service.py`) para categorizar las vulnerabilidades en: **Baja, Media, Alta o Crítica**. Incorpora una capa de seguridad ("No técnico"/"Informativa") para bloquear falsos positivos y textos irrelevantes.

### 2. Análisis Semántico (NER)
Arquitectura híbrida que combina el modelo `wikineural` de Hugging Face con un motor de Expresiones Regulares (Regex) en Python para garantizar una precisión del **100% en la detección de IPs y Puertos**, además de extraer software afectado y vectores de ataque.

### 3. Generación de Resumen Ejecutivo
Para prevenir alucinaciones de IA, se ha descartado el uso de modelos generativos pesados (como mT5). En su lugar, se emplea lógica determinista basada en los datos extraídos (Regex) y plantillas dinámicas según el nivel de severidad.

### 4. Endpoints Clave (`router.py`)
- **Autenticación:** `/users/login` y `/register`. Manejo de sesiones seguras.
- **Gestión de Usuarios (CRUD):** Endpoints GET, POST, PUT y DELETE para control de roles (Analista, Gerente, Administrador).
- **Dashboard y Estadísticas:** `/dashboard/stats` para agregación de datos y métricas visuales.

### 5. Auditoría e Historial
Todo texto enviado, usuario que realiza la consulta, y resultado devuelto es registrado inmutablemente en la base de datos **PostgreSQL** mediante **SQLAlchemy**, asegurando la trazabilidad de las acciones.

## Rendimiento y Privacidad (Offline)
- **Aislamiento Total:** El sistema garantiza la privacidad al procesar todo localmente de forma *offline*. Los logs, que pueden contener IPs reales o tokens, nunca viajan a APIs externas.
- **Eficiencia:** Sistema optimizado para inferencia rápida mediante modelos ligeros, garantizando el análisis sin requerir hardware con GPUs masivas ni saturar la memoria RAM.

## Requisitos e Instalación
1. Clonar el repositorio.
2. Crear un entorno virtual: `python -m venv venv`
3. Activar el entorno virtual e instalar las dependencias: `pip install -r requirements.txt`
5. Ejecutar el servidor FastAPI: `uv run uvicorn main:app --reload`
6. Acceder a la documentación interactiva en `http://localhost:8000/docs`.
