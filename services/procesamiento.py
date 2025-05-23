import tempfile
import os
from tools.pdf_loader import extract_text_from_pdf
from agents.requisitos_analyst import get_requisitos_analyst_agent, build_requisitos_analysis_task
from crewai import Crew
from dotenv import load_dotenv
import json
import re

load_dotenv()

def procesar_pdf_con_modelo(file_bytes: bytes, model: str) -> dict:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    texto = extract_text_from_pdf(tmp_path)
    os.remove(tmp_path)

    agent = get_requisitos_analyst_agent(model)
    task = build_requisitos_analysis_task(texto, agent)
    crew = Crew(agents=[agent], tasks=[task], verbose=False)

    # output = str(crew.kickoff())

    # return {
    #     "modelo_usado": model,
    #     "analisis": output
    # }

    output_raw = str(crew.kickoff())
    try:
        json_puro = extraer_json_de_respuesta(output_raw)
        parsed_json = json.loads(json_puro)
    except Exception as e:
        raise ValueError(f"❌ No se pudo extraer un JSON válido.\nSalida:\n{output_raw}\n\nError: {str(e)}")

    return {
        "modelo_usado": model,
        "analisis": parsed_json
    }

def extraer_json_de_respuesta(texto: str) -> str:
    """
    Extrae el primer bloque JSON válido desde una respuesta que puede tener markdown o texto adicional.
    """
    match = re.search(r'\{[\s\S]+\}', texto)
    if match:
        return match.group(0)
    raise ValueError("No se encontró un bloque JSON válido en la respuesta del modelo.")