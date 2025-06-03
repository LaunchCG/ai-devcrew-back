from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from requests.auth import HTTPBasicAuth
from services.procesamiento import procesar_archivo_con_modelo
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
from services.jira_publicador import publicar_tickets_en_jira
from agents.calidad_analyst import get_qa_agent
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


@app.post("/validate-jira-stories")
async def validate_jira_stories(data: dict):
    try:
        model = data.get("model", "gpt-4") 
        ids = data.get("ids", [])

        if not ids:
            raise ValueError("Debes enviar una lista de IDs de Jira")

        detalles = obtener_detalles_issues(ids)
        agente = get_qa_agent(model)

        # Cargar y preparar template
        with open("prompts/qa_review_prompt.txt", "r", encoding="utf-8") as f:
            template = Template(f.read())

        resultados = []
        for historia in detalles:
            if historia.get("error"):
                resultados.append({
                    "story": historia["id"],
                    "validation": "ERROR",
                    "suggestion": historia["error"]
                })
                continue

            prompt = template.render(
                title=historia["summary"],
                description=historia["description"],
                id=historia["id"]
            )

            task = Task(
                description=prompt,
                agent=agente,
                expected_output="Un JSON con el análisis de la historia",
            )
            crew = Crew(agents=[agente], tasks=[task])
            salida = crew.kickoff()

            # Intentar parsear solo la parte útil
            # raw_output = salida.get("raw") or salida.get("tasks_output", [{}])[0].get("raw", "")
            # Manejo de salida como string
            if hasattr(salida, "raw"):
                raw_output = salida.raw
            elif hasattr(salida, "tasks_output") and salida.tasks_output:
                raw_output = salida.tasks_output[0].raw
            else:
                raw_output = str(salida)


            raw_output = raw_output.strip()

            if raw_output.startswith("```json"):
                raw_output = raw_output.replace("```json", "").strip()
            if raw_output.endswith("```"):
                raw_output = raw_output[:-3].strip()

            try:
                parsed = json.loads(raw_output)
                resultados.append(parsed)
            except Exception as e:
                resultados.append({
                    "story": historia["id"],
                    "validation": "ERROR",
                    "suggestion": f"No se pudo interpretar la respuesta del agente: {str(e)}",
                    "raw_output": raw_output
                })

        return resultados

    except Exception as e:
        return {"error": str(e)}

@app.get("/get-all-stories")
async def get_all_stories(board_name: str):
    try:
        result = get_issues_from_board(board_name)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))