import os
import requests
from requests.auth import HTTPBasicAuth

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {
    "Accept": "application/json"
}

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
