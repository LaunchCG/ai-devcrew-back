from crewai import Agent
from tools.github_issues_tool import get_github_issues_tool

def get_github_issues_agent(llm) -> Agent:
    return Agent(
        role="GitHub Issue Analyst",
        goal="Analyze GitHub issues to extract insights and highlight important patterns",
        backstory="You are an expert GitHub maintainer who understands repositories and prioritizes issues for teams.",
        tools=[get_github_issues_tool],
        allow_delegation=False,
        verbose=True,
        llm=llm
    )
