from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import joblib
import pandas as pd
import os

model = None
MODEL_PATH = "models/modelo_campeon_capv.pkl"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("[OK] Modelo campeón cargado correctamente en memoria mediante lifespan.")
    else:
        model = None
        print("[!] Advertencia: No se encontró el archivo del modelo en la ruta especificada.")
    yield
    print("[*] Cerrando aplicación y liberando recursos...")

app = FastAPI(
    title="API MLOps - Predicción de Costes de Reforma (CAPV)",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": "MLOps CAPV Reformas",
        "model_loaded": model is not None
    }

@app.post("/predict")
def predict(data: dict):
    if model is None:
        raise HTTPException(status_code=500, detail="El modelo no está cargado en el servidor.")
    try:
        df_input = pd.DataFrame([data])
        prediction = model.predict(df_input)
        return {"coste_estimado_eur": float(prediction[0])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la inferencia: {str(e)}")
