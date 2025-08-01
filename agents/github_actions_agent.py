from crewai import Agent
from tools.get_github_workflow_runs_tool import get_github_workflow_runs_tool

def get_github_actions_agent(llm) -> Agent:
    return Agent(
        role="GitHub Actions Inspector",
        goal="Analyze recent GitHub Actions workflows and detect failures or performance issues",
        backstory="You are a DevOps specialist helping improve CI/CD pipelines based on workflow history.",
        tools=[get_github_workflow_runs_tool],
        allow_delegation=False,
        verbose=True,
        llm=llm
    )
