from crewai import Agent, Task
from dotenv import load_dotenv
import os

load_dotenv()

def get_requisitos_analyst_agent(model: str) -> Agent:
    return Agent(
        role="Analista de requisitos",
        goal="Analizar especificaciones técnicas para generar hitos, historias de usuario y diseño de base de datos",
        backstory="Sos un experto funcional con capacidad de estructurar requisitos para desarrollo.",
        verbose=True,
        allow_delegation=False,
        llm=model
    )

def build_requisitos_analysis_task(texto: str, agent: Agent) -> Task:
    prompt_path = "prompts/requisitos_prompt.txt"
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    full_prompt = prompt_template.replace("{input_text}", texto.strip())

    return Task(
        description=full_prompt,
        expected_output="Hitos, historias de usuario y diseño de base de datos si aplica",
        agent=agent
    )
