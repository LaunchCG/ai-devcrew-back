import json
from crewai import Crew, Task
from jinja2 import Template
from agents.qa_analyst import get_qa_agent
from services.jira_issues import obtener_detalles_issues
from tools.text_utils import extract_first_json_block


def validate_jira_stories_logic(story_ids, model="gpt-4"):
    issue_details = obtener_detalles_issues(story_ids)
    qa_agent = get_qa_agent(model)

    with open("prompts/qa_review_prompt.txt", "r", encoding="utf-8") as f:
        prompt_template = Template(f.read())

    results = []

    for issue in issue_details:
        if issue.get("error"):
            results.append({
                "story": issue["id"],
                "validation": "ERROR",
                "suggestion": issue["error"]
            })
            continue

        rendered_prompt = prompt_template.render(
            title=issue["summary"],
            description=issue["description"],
            id=issue["id"]
        )

        task = Task(
            description=rendered_prompt,
            agent=qa_agent,
            expected_output="A JSON with the story evaluation",
        )
        crew = Crew(agents=[qa_agent], tasks=[task])
        output = crew.kickoff()

        # Get raw output
        if hasattr(output, "raw"):
            raw_output = output.raw
        elif hasattr(output, "tasks_output") and output.tasks_output:
            raw_output = output.tasks_output[0].raw
        else:
            raw_output = str(output)

        # Clean and parse JSON
        try:
            cleaned_json = extract_first_json_block(raw_output)
            parsed = json.loads(cleaned_json)
            results.append(parsed)
        except Exception as e:
            results.append({
                "story": issue["id"],
                "validation": "ERROR",
                "suggestion": f"Could not parse agent response as JSON: {str(e)}",
                "raw_output": raw_output
            })

    return results
