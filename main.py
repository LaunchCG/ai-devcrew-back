from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from requests.auth import HTTPBasicAuth
from services.procesamiento import procesar_archivo_con_modelo
from fastapi.responses import JSONResponse, FileResponse
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
from services.jira_publicador import publicar_tickets_en_jira
from services.jira_issues import get_issues_from_board, delete_issue_request
from services.jira_commenter import post_comments_to_jira
from services.prompt_manager import get_prompt_byname, addorupdate_prompt_byname
from typing import List
from models.story_review_comment import StoryReview
from services.domain_model_extractor import extract_domain_model_from_stories

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
async def get_all_stories():
    try:
        result = get_issues_from_board()
        return JSONResponse(content=result)
    except Exception as e:
        return {"error": str(e)}
    
@app.delete("/delete-issue")
async def delete_issue(issue_key: str):
    try:
        response = delete_issue_request(issue_key)
        if response.status_code == 204:
            return JSONResponse(content={"message": "✅ Issue removed successfully."})
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        return {"error": str(e)}
    
@app.post("/comment-review-results")
async def comment_review_results(data: List[StoryReview]):

    try:
        return post_comments_to_jira(data)
    except Exception as e:
        return {"error": str(e)}

@app.get("/get-prompt")
async def get_prompt(prompt_name: str):
    try:
        result = get_prompt_byname(prompt_name)
        return JSONResponse(content=result)
    except Exception as e:
        return {"error": str(e)}
    
@app.post("/add-or-update-prompt")
async def addorupdate_prompt(prompt_name: str, prompt_value: str):
    try:
        return addorupdate_prompt_byname(prompt_name, prompt_value)
    except Exception as e:
        return {"error": str(e)}

@app.post("/extract-domain-model")
async def extract_domain_model(data: dict):
    try:
        model = data.get("model", "gpt-4")
        story_ids = data.get("ids", [])
        if not story_ids:
            raise ValueError("You must send a list of Jira Story IDs")

        return extract_domain_model_from_stories(story_ids, model)
    except Exception as e:
        return {"error": str(e)}

@app.post("/download-terraform")
async def download_terraform(data: dict):
    folder = "terraform"
    file_name = "main.tf"
    file_path = os.path.join(folder, file_name)

    if not os.path.isfile(file_path):
        return {"error": f"File {file_path} not found."}

    return FileResponse(
        path=file_path,
        media_type="application/json",
        filename=file_name
    )