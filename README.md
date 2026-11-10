[README.md](https://github.com/user-attachments/files/34624577/README.md)
# Sistema MLOps End-to-End: Predicción de Costes de Reforma Inmobiliaria (CAPV)

Este repositorio contiene una solución MLOps orientada a producción para la predicción automatizada y determinista de costes de reformas en la Comunidad Autónoma del País Vasco (CAPV). El sistema implementa un flujo completo: ingesta de datos, validación estricta con Pydantic V2, limpieza multivariable, seguimiento y registro en MLflow, evaluación con Quality Gate, servicio mediante FastAPI y automatización de CI/CD con GitHub Actions.

---

## 1\. Caso de Uso y Dataset

El objetivo del sistema es predecir el coste total de obra (`coste_total_obra` en EUR) a partir de características físicas, energéticas, logísticas y fiscales de inmuebles sintéticos validados contra fuentes públicas de la CAPV:

* **Open Data Euskadi**: Certificación de Eficiencia Energética (CEE), ITE y catastro.  
* **Eustat**: Índices comarcales de edificación, precios sectoriales y coeficientes forales.  
* **Udalmap**: Densidad urbana e impuesto municipal de construcciones (ICIO).  
* **Ihobe**: Distancias a plantas de tratamiento de Residuos de Construcción y Demolición (RCD) y restricciones de Zonas de Bajas Emisiones (ZBE).

---

## 2\. Estructura del Repositorio y Separación de Responsabilidades

Siguiendo los requisitos de arquitectura modular MLOps, el repositorio organiza sus componentes en carpetas dedicadas:

```
proyecto-mlops-capv/
├── .github/
│   └── workflows/
│       └── ci.yml                   # Orquestación de CI/CD (GitHub Actions)
├── data/
│   ├── raw/                         # Ingesta cruda (dataset_reformas_capv_oficial.csv)
│   ├── processed/                   # Datasets limpios (dataset_reformas_capv_limpio.csv)
│   ├── logs/                        # Historial HTTP y registros de auditoría
│   └── audits/                      # Informes vectoriales de expedientes
├── models/
│   └── modelo_campeon_capv.pkl       # Artefacto del modelo campeón servido por la API
├── src/
│   ├── __init__.py                  # Descriptor del paquete modular
│   └── main.py                      # Código de servicio FastAPI, endpoints y middleware
├── logs/
│   └── pipeline_status.log          # Trazabilidad local del pipeline
├── requirements.txt                 # Lista acotada de dependencias
└── README.md                        # Documentación principal de despliegue
```

---

## 3\. Guía de Instalación y Despliegue

### 3.1. Prerrequisitos

* Python 3.10 o superior \[cite: 3\].  
* Git \[cite: 3\].

### 3.2. Despliegue Local y en Entorno Google Colab

El sistema está adaptado tanto para ejecución local como para su despliegue dentro de una máquina virtual en **Google Colab**.

1. **Clonar el repositorio o inicializar entorno:**

```sh
git clone https://github.com/tu-usuario/proyecto-mlops-capv.git
cd proyecto-mlops-capv
```

2. **Instalar dependencias:**

```sh
pip install -r requirements.txt
```

---

## 4\. Ejecución del Pipeline Completo (Extracción, Validación, Limpieza y Entrenamiento)

```sh
python src/main.py
```

### Flujo Interno de Ejecución:

1. **Extracción**: Genera e ingesta los datos en `data/raw/dataset_reformas_capv_oficial.csv` \[cite: 3\].  
2. **Validación (Fail-Fast)**: Aplica contrato estricto con **Pydantic V2** \[cite: 3\].  
3. **Limpieza**: Aplica filtrado IQR univariante e **Isolation Forest** multivariable \[cite: 3\].  
4. **Entrenamiento y MLflow**: Benchmarking comparativo con validación cruzada (\$K=10\$) \[cite: 3\].  
5. **Quality Gate y Promoción**:  
   * **Modelo Campeón Seleccionado**: **Ridge Regression** (\$R^2 \= 0.9715\$, \$\\text{MAE} \= 2.339,38\\ \\text{€}\$) \[cite: 3\].  
   * Exportado a `models/modelo_campeon_capv.pkl` \[cite: 3\].

---

## 5\. Servicio de la API (FastAPI) y Pruebas de Endpoints

### 5.1. Endpoints Oficiales

* `GET /`: Comprobación de estado general \[cite: 3\].  
* `GET /health`: Comprobación de salud / readiness \[cite: 3\].  
* `GET /model-info`: Metadatos del modelo campeón y características \[cite: 3\].  
* `POST /predict`: Generación de inferencia en tiempo real con validación Pydantic V2 \[cite: 3\].

---

## 6\. Manejo de Errores y Calidad HTTP

* **200 OK**: Solicitud exitosa y predicción calculada \[cite: 3\].  
* **422 Unprocessable Entity / 400 Bad Request**: Datos de entrada inválidos rechazados por Pydantic \[cite: 3\].  
* **500 Internal Server Error**: Excepción controlada en el pipeline de inferencia \[cite: 3\].

---

## 7\. Pruebas Interactivas y Telemetría

Cada petición al endpoint `/predict` es registrada por un middleware HTTP que asigna un `X-Request-ID`, mide la latencia en milisegundos y persiste la operación en `data/logs/historial_inferencias_api.csv` \[cite: 3\].

---

## 8\. Automatización CI/CD con GitHub Actions

Configurado en `.github/workflows/ci.yml` para ejecutar pruebas de humo (*Smoke Tests*) automáticas en runners limpios de Ubuntu ante cada `push` o `pull_request` \[cite: 3\].

---

## 9\. Arquitectura de Despliegue, Túneles y Monitorización

* **Acceso mediante Túneles (Google Colab)**: Se ha integrado con éxito un sistema de tunelización mediante **localtunnel** para exponer la API y permitir el acceso interactivo al **Swagger UI** (`/docs`) desde el navegador externo, manteniendo plena compatibilidad con el despliegue en bucle local (`127.0.0.1:8000`).  
* **Estado de OpenObserve**: Durante la fase de arquitectura se valoró la incorporación de OpenObserve como HUB centralizado de monitorización de los diferentes endpoints; sin embargo, esta herramienta **fue descartada para este proyecto por elección del departamento ejecutivo**.
