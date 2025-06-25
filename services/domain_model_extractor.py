import json
from crewai import Task, Crew
from jinja2 import Template
from agents.domain_modeler import get_domain_modeler_agent
from tools.text_utils import extract_first_json_block
from services.jira_issues import obtener_detalles_issues
from services.prompt_manager import get_prompt_byname

def extract_domain_model_from_stories(story_ids: list, model: str = "gpt-4"):
    stories = obtener_detalles_issues(story_ids)
    agent = get_domain_modeler_agent(model)

    # Concatenar las historias en texto
    stories_text = ""
    for s in stories:
        stories_text += f"- {s['summary']}: {s['description']}\n"

    # Cargar el prompt desde JSON
    prompt_template = get_prompt_byname("DOMAIN_MODELING_PROMPT")
    prompt = Template(prompt_template).render(user_stories=stories_text)

    task = Task(
        description=prompt,
        agent=agent,
        expected_output="A JSON structure listing domain entities, attributes, and relationships."
    )
    crew = Crew(agents=[agent], tasks=[task])
    output = crew.kickoff()

    # Extraer JSON limpio
    raw = output.raw if hasattr(output, "raw") else str(output)
    try:
        json_clean = extract_first_json_block(raw)
        return json.loads(json_clean)
    except Exception as e:
        return {"error": str(e), "raw_output": raw}
