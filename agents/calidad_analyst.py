from crewai import Agent

def get_qa_agent(model):
    return Agent(
        role="Analista de calidad de producto",
        goal="Revisar historias de usuario y validar si cumplen con criterios de calidad",
        backstory="Sos un experto en metodologías ágiles y redacción de historias claras y efectivas.",
        verbose=True,
        allow_delegation=False,
        llm=model
    )
