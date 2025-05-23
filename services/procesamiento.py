import tempfile
import os
from tools.pdf_loader import extract_text_from_pdf
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
import litellm

load_dotenv()

def procesar_pdf_con_modelo(file_bytes: bytes, model: str) -> dict:
    import tempfile
    from crewai import Agent, Task, Crew
    from tools.pdf_loader import extract_text_from_pdf

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    texto = extract_text_from_pdf(tmp_path)
    os.remove(tmp_path)

    agent = Agent(
        role="Analista de requisitos",
        goal="Analizar especificaciones técnicas...",
        backstory="Sos un experto funcional con capacidad de estructurar requisitos para desarrollo.",
        verbose=True,
        allow_delegation=False,
        llm=model  # ← simplemente el nombre del modelo
    )

    prompt = f"""
Sos un experto en análisis de software. Te paso las especificaciones técnicas de un proyecto.

Tu tarea es:
1. Detectar los hitos principales del proyecto (máximo 5).
2. Para cada hito, generar 1 o más historias de usuario en formato:

Como [tipo de usuario], quiero [acción], para [beneficio].

3. Si es necesario, describí una estructura básica de base de datos con tablas y relaciones.
4. Si hay lógica que lo amerite, generá un diagrama de flujo o de componentes (en texto o Mermaid.js).

Texto de entrada:
"{texto}"
"""

    task = Task(
        description=prompt,
        expected_output="Hitos, historias de usuario y diseño de base de datos si aplica",
        agent=agent
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    # output = crew.kickoff()
    output = str(crew.kickoff())
    return {
        "modelo_usado": model,
        "analisis": output
    }
