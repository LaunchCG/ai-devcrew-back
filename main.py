from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from services.procesamiento import procesar_archivo_con_modelo
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.post("/process-request")
async def process_request(file: UploadFile = File(...), model: str = Form(...)):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF o Word (.docx)")


    try:
        content = await file.read()
        resultado = resultado = procesar_archivo_con_modelo(content, model, file)
        return JSONResponse(content=resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
