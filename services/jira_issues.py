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
                        detalles.append({
                            "id": issue["id"],
                            "key": issue["key"],
                            "summary": issue["fields"]["summary"],
                            "description": issue["fields"]["description"] or "",
                            "project": issue["fields"]["project"]["name"]
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