import os
import requests
from requests.auth import HTTPBasicAuth
import hashlib

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {
    "Accept": "application/json"
}

def generar_hash(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

def obtener_detalles_issues(issue_ids: list[str]) -> list[dict]:
    detalles = []

    for issue_id in issue_ids:
        url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{issue_id}"
        response = requests.get(url, headers=headers, auth=auth)
        if response.status_code == 200:
            data = response.json()
            detalles.append({
                "id": issue_id,
                "summary": data["fields"]["summary"],
                "description": data["fields"]["description"]["content"][0]["content"][0]["text"] if data["fields"]["description"] else "",
                "raw": data
            })
        else:
            detalles.append({
                "id": issue_id,
                "error": f"Status {response.status_code}",
                "raw": response.text
            })

    return detalles

def get_issues_from_board() -> list[dict]:
    detalles = []

    url = f"https://{JIRA_DOMAIN}/rest/agile/1.0/board"
    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code == 200:
        boards = response.json()["values"]
        if boards:
            for board in boards:
                url = f"https://{JIRA_DOMAIN}/rest/agile/1.0/board/{board['id']}/backlog"

                response = requests.get(url, headers=headers, auth=auth)

                if response.status_code == 200:
                    issues = response.json().get("issues", [])
                    for issue in issues:
                        ticket_updated = "false"
                        labels = issue["fields"].get("labels", [])
                        hash_label = next((label for label in labels if label.startswith("hash-")), None)
                        hash_issue = "hash-"+generar_hash(issue["fields"]["summary"]+(issue["fields"]["description"] or ""))
                        print(issue["fields"]["summary"]+(issue["fields"]["description"] or ""))
                        if (hash_label != hash_issue):
                            ticket_updated = "true"

                        detalles.append({
                            "id": issue["id"],
                            "key": issue["key"],
                            "summary": issue["fields"]["summary"],
                            "description": issue["fields"]["description"] or "",
                            "project": issue["fields"]["project"]["name"],
                            "ticket_updated": ticket_updated
                        })
                else:
                    detalles.append({
                        "error": f"Status {response.status_code}",
                        "raw": response.text
                    })
        else:
            print("❌ Couldn't find a projects in this domain.")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

    return detalles

def delete_issue_request(issue_key: str):
    url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{issue_key}"
    response = requests.delete(url, headers=headers, auth=auth)
    return response