# services/github_issues.py
from crewai import Task, Crew
from agents.github_issues_agent import get_github_issues_agent
from jinja2 import Template
from services.prompt_manager import get_prompt_byname

def get_github_issues(token: str, repo: str, model: str = "gpt-4"):
    agent = get_github_issues_agent(model)

    prompt_template = get_prompt_byname("GITHUB_ISSUES_PROMPT")
    context_prompt = Template(prompt_template).render(token=token, repo=repo)

    task = Task(
        description=context_prompt,
        agent=agent,
        expected_output="Either a summary of GitHub issues with insights, or a clear statement if there are no issues to analyze."
    )

    crew = Crew(
        agents=[agent],
        tasks=[task]
    )

    result = crew.kickoff()
    return str(result)