from crewai import Agent

def get_qa_agent(model):
    return Agent(
        role="Product Quality Analyst",
        goal="Review user stories and validate if they meet quality standards",
        backstory="You are an expert in Agile methodologies with strong skills in writing clear and effective user stories.",
        verbose=True,
        allow_delegation=False,
        llm=model
    )
