import requests
from requests.auth import HTTPBasicAuth
import os

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def crear_issue(summary: str, description: str, issue_type: str = "Story"):
    url = f"https://{JIRA_DOMAIN}/rest/api/3/issue"
    payload = {
        "fields": {
            "project": {
                "key": JIRA_PROJECT_KEY
            },
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "text": description,
                                "type": "text"
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": issue_type
            }
        }
    }

    response = requests.post(url, json=payload, headers=headers, auth=auth)
    return response.status_code, response.json()

def publicar_tickets_en_jira(analisis: dict):
    resultados = []
    tickets = analisis.get("tickets", [])

    for ticket in tickets:
        summary = ticket.get("summary")
        tipo = ticket.get("tipo", "Story")
        criterios = ticket.get("criterios_de_aceptacion", [])
        descripcion = ticket.get("description", "")

        criterios_md = "\n\n**Criterios de aceptación:**\n" + "\n".join(f"- {c}" for c in criterios) if criterios else ""
        descripcion_final = descripcion.strip() + criterios_md

        status, res = crear_issue(summary=summary, description=descripcion_final, issue_type=tipo)
        resultados.append({
            "summary": summary,
            "status": status,
            "response": res
        })

    return resultados
