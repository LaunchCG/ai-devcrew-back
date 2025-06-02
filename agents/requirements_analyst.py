from crewai import Agent, Task
from dotenv import load_dotenv
import os

load_dotenv()

def get_requirements_analyst_agent(model: str) -> Agent:
    return Agent(
        role="Requirements Analyst",
        goal="Analyze technical specifications to generate milestones, user stories, and database design",
        backstory="You are a functional expert with strong skills in structuring requirements for software development.",
        verbose=True,
        allow_delegation=False,
        llm=model
    )

def build_requirements_analysis_task(text: str, agent: Agent) -> Task:
    prompt_path = "prompts/requirements_prompt.txt"
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    full_prompt = prompt_template.replace("{input_text}", text.strip())

    return Task(
        description=full_prompt,
        expected_output="Milestones, user stories, and database design if applicable",
        agent=agent
    )
