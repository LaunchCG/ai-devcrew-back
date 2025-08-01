from crewai.tools import tool
import requests

@tool("Get GitHub Actions Workflow Runs")
def get_github_workflow_runs_tool(repo: str, token: str) -> str:
    """Fetches the latest GitHub Actions workflow runs and returns a summary."""
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=10"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"GitHub API error {response.status_code}: {response.text}")

    data = response.json()
    runs = data.get("workflow_runs", [])

    if not runs:
        return "No recent workflow runs found."

    summary = []
    for run in runs:
        summary.append(
            f"- Workflow: {run['name']} | Status: {run['status']} | Conclusion: {run.get('conclusion', 'N/A')} | Duration: {run['run_started_at']} → {run['updated_at']}"
        )

    return "\n".join(summary)