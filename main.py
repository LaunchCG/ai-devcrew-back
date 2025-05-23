from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from services.procesamiento import procesar_pdf_con_modelo
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.post("/process-request")
async def process_request(file: UploadFile = File(...), model: str = Form(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    try:
        content = await file.read()
        resultado = procesar_pdf_con_modelo(content, model)
        return JSONResponse(content=resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
