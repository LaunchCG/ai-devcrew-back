from crewai.tools import tool
import requests

@tool("Get GitHub Issues")
def get_github_issues_tool(repo: str, token: str) -> str:
    """Fetches issues from the given GitHub repository and returns them in plain text format."""
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"GitHub API error {response.status_code}: {response.json()}")

    issues = response.json()
    filtered = [i for i in issues if "pull_request" not in i]

    if not filtered:
        return "✅ This repository currently has no issues to analyze."


    # Transform issues to plain text summary
    return "\n".join(
        f"- #{issue['number']}: {issue['title']} - {issue.get('body', '')[:100]}"
        for issue in filtered
    )
