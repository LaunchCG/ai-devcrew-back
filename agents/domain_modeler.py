from crewai import Agent

def get_domain_modeler_agent(model: str) -> Agent:
    return Agent(
        role="Domain Model Expert",
        goal="Analyze multiple user stories and extract the domain entities and relationships",
        backstory=(
            "You are a software architect with deep expertise in analyzing business requirements and identifying domain entities, "
            "their attributes, and relationships. You help development teams by producing clean and normalized conceptual models."
        ),
        verbose=True,
        allow_delegation=False,
        llm=model
    )
