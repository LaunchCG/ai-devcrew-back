from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from requests.auth import HTTPBasicAuth
from services.procesamiento import procesar_archivo_con_modelo
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
from services.jira_publicador import publicar_tickets_en_jira
from agents.qa_analyst import get_qa_agent
from crewai import Task, Crew
from services.jira_issues import obtener_detalles_issues
from services.jira_issues import get_issues_from_board
import json
import re
from jinja2 import Template


load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Podés cambiar esto a ["http://localhost:3000"] si querés restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

@app.post("/publish-to-jira")
async def publish_to_jira(data: dict = Body(...)):
    try:
        analisis = data.get("analisis", data)  # soporta JSON completo o solo el nodo
        resultado = publicar_tickets_en_jira(analisis)
        return {"resultado": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jira-user")
async def get_jira_user():
    from services.jira_publicador import auth, headers, JIRA_DOMAIN
    import requests

    try:
        url = f"https://{JIRA_DOMAIN}/rest/api/3/myself"
        email = os.getenv("JIRA_EMAIL")
        api_token = os.getenv("JIRA_API_TOKEN")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, auth=HTTPBasicAuth(email, api_token))
        return {
            "url": url,
            "status_code": response.status_code,
            "text": response.text,
            "user": email,
            "domain": JIRA_DOMAIN            
        }

    except Exception as e:
        return {"error": str(e)}


from services.story_validation import validate_jira_stories_logic

@app.post("/validate-jira-stories")
async def validate_jira_stories(data: dict):
    try:
        model = data.get("model", "gpt-4")
        story_ids = data.get("ids", [])
        if not story_ids:
            raise ValueError("You must send a list of Jira Story IDs")

        return validate_jira_stories_logic(story_ids, model)

    except Exception as e:
        return {"error": str(e)}


@app.get("/get-all-stories")
async def get_all_stories(board_name: str):
    try:
        result = get_issues_from_board(board_name)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))