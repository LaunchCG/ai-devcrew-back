from crewai import Task, Crew
from jinja2 import Template
from services.prompt_manager import get_prompt_byname
from agents.github_actions_agent import get_github_actions_agent

def analyze_github_actions(token: str, repo: str, model: str = "gpt-4"):
    agent = get_github_actions_agent(model)

    prompt_template = get_prompt_byname("GITHUB_ACTIONS_PROMPT")
    context_prompt = Template(prompt_template).render(token=token, repo=repo)

    task = Task(
        description=context_prompt,
        agent=agent,
        expected_output="A structured summary of recent GitHub Actions workflows including issues or improvement suggestions."
    )

    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()
    return str(result)