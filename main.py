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

        resultados = []
        for historia in detalles:
            if historia.get("error"):
                resultados.append({
                    "story": historia["id"],
                    "validation": "ERROR",
                    "suggestion": historia["error"]
                })
                continue

            prompt = f"""
                    Te paso la descripción de una historia de usuario:

                    Título: {historia['summary']}
                    Descripción: {historia['description']}

                    Tu tarea es validar si esta historia cumple con criterios de calidad y claridad para ser implementada.

                    Devolvé un JSON con este formato:

                    {{
                    "story": "{historia['id']}",
                    "validation": "OK o ERROR",
                    "suggestion": "Una sugerencia concreta de mejora si es necesario"
                    }}
                    """

            task = Task(
                description=prompt,
                agent=agente,
                expected_output="Un JSON con el análisis de la historia",
            )
            crew = Crew(agents=[agente], tasks=[task])
            salida = crew.kickoff()
            resultados.append(salida)

        return {"resultados": resultados}

    except Exception as e:
        return {"error": str(e)}
