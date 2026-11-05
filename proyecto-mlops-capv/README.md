# MLOps Pipeline: Estimación de Costes de Reforma Inmobiliaria en la CAPV

Este repositorio contiene una solución end-to-end de MLOps para la predicción del coste total de reformas de viviendas en la Comunidad Autónoma del País Vasco (CAPV). El sistema integra ingesta de fuentes públicas institucionales, validación mediante contratos de datos estrictos, filtrado de anomalías multivariable, registro de experimentos en MLflow, servicio de inferencia con FastAPI y automatización de CI/CD mediante GitHub Actions.

## 1. Caso de Uso y Fuentes de Datos

El objetivo del sistema es predecir el coste total de obra (EUR) a partir de características físicas, fiscales y logísticas del inmueble en los tres territorios históricos (Araba, Bizkaia y Gipuzkoa).

* **Open Data Euskadi**: Certificación de Eficiencia Energética (CEE), datos catastrales y antigüedad de inspección (ITE).
* **Eustat**: Índices comarcales de edificación y mano de obra sectorial.
* **Udalmap**: Tipos impositivos municipales (ICIO).
* **Ihobe**: Distancias a vertederos autorizados de Residuos de Construcción y Demolición (RCD) y condicionantes de ZBE.

## 2. Estructura del Repositorio

```text
MLOps_Reformas_CAPV/
├── .github/
│   └── workflows/
│       └── ci.yml             # Workflow de GitHub Actions (CI/CD)
├── data/
│   ├── raw/                   # Datos crudos de ingesta
│   ├── processed/             # Datasets limpios y transformados
│   └── logs/                  # Trazabilidad y logs de ejecución
├── models/
│   ├── modelo_campeon_capv.pkl # Artefacto del modelo campeón cargado por la API
│   └── mlruns/                # Tracking de experimentos con MLflow
├── src/
│   ├── __init__.py
│   ├── data_extraction.py     # Ingesta desde fuentes de Open Data
│   ├── data_validation.py     # Validación de contratos con Pydantic V2 (Fail-Fast)
│   ├── data_cleaning.py       # Filtrado IQR y Detección de anomalías (Isolation Forest)
│   ├── model_training.py      # Entrenamiento y tracking con MLflow
│   ├── model_evaluation.py    # Evaluador de Quality Gate y Model Registry
│   └── api.py                 # Servicio API REST expuesto con FastAPI
├── backups/                   # Respaldo centralizado de snapshots
├── notebook_exploratorio.ipynb # Cuaderno interactivo de análisis (EDA)
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Documentación principal
```

## 3. Instalación y Configuración del Entorno

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/tu-usuario/MLOps_Reformas_CAPV.git
   cd MLOps_Reformas_CAPV
   ```

2. **Crear y activar un entorno virtual:**

   ```bash
   python -m venv venv
   source venv/bin/activate   # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias:**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## 4. Ejecución del Pipeline Secuencial

Puedes ejecutar el pipeline paso a paso desde la terminal:

```bash
# 1. Extracción de datos crudos
python src/data_extraction.py

# 2. Validación de esquemas (Fail-Fast)
python src/data_validation.py

# 3. Limpieza y filtrado de anomalías (IQR + Isolation Forest)
python src/data_cleaning.py

# 4. Entrenamiento y tracking en MLflow
python src/model_training.py

# 5. Evaluador de Quality Gate y asignación del modelo campeón
python src/model_evaluation.py
```

## 5. Criterios de Selección y Quality Gate

El pipeline incorpora una puerta de calidad (Quality Gate) sobre el coeficiente de determinación ($R^2$):

* **Umbral de Calidad**: Coeficiente $R^2 \ge 0.85$ obtenido mediante validación cruzada ($K=10$ Folds).
* **Resultados de Benchmarking**:
  * **Ridge Regression** (*Modelo Campeón*): $R^2 = 0.9680$ | $MAE = 3.270,15 \text{ EUR}$
  * **Random Forest Regressor**: $R^2 = 0.9421$
  * **Gradient Boosting Regressor**: $R^2 = 0.9510$
* **Promoción**: El modelo seleccionado se exporta a `models/modelo_campeon_capv.pkl` y recibe el alias `champion` en MLflow.

## 6. Servicio API (FastAPI)

Para iniciar el servidor local de inferencia:

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

### Endpoints Oficiales:

1. **`GET /health`** (Comprobación de Estado)
   * **Respuesta (`200 OK`)**: `{"status": "ok"}`

2. **`GET /model-info`** (Inspección de Metadatos)
   * **Respuesta (`200 OK`)**:
     ```json
     {
       "model_name": "Ridge_CAPV_Champion",
       "version": "1.0.0",
       "alias": "champion",
       "quality_r2": 0.9680
     }
     ```

3. **`POST /predict`** (Generación de Inferencia)
   * **Payload (`JSON`)**:
     ```json
     {
       "superficie_m2": 85.5,
       "antiguedad_anos": 40,
       "distancia_vertedero_rcd_km": 12.3,
       "calificacion_energetica": "E",
       "municipio": "Bilbao"
     }
     ```
   * **Respuesta Exitosa (`200 OK`)**:
     ```json
     {
       "coste_estimado_eur": 42150.80,
       "model_version": "1.0.0",
       "status": "success"
     }
     ```
   * **Respuesta de Error de Entrada (`422 Unprocessable Entity`)**: Ocurre ante datos mal formados o tipos incorrectos.
   * **Respuesta de Servicio No Disponible (`503 Service Unavailable`)**: Ocurre si el archivo `.pkl` del modelo no está presente.

## 7. Integración Continua (CI/CD)

El archivo `.github/workflows/ci.yml` automatiza la ejecución del pipeline en GitHub Actions con cada `push` o `pull_request` a las ramas `main` o `master`.

**Pasos del Flujo Integrado:**

1. Inicialización de máquina runner de Ubuntu con Python 3.10.
2. Instalación de paquetes de `requirements.txt`.
3. Ejecución secuencial en orden: Extracción -> Validación -> Limpieza -> Entrenamiento -> Evaluación.
4. Verificación de la presencia del artefacto `.pkl` en `models/`.