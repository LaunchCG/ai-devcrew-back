# ai-devcrew-back
AI Software Development Crew Agents - Backend

## Requisitos

- Python 3.10+
- FastAPI
- CrewAI
- API key de OpenAI

## Instalación

```bash
git clone https://github.com/LaunchCG/ai-devcrew-back.git
cd ai-devcrew-back
python -m venv venv
venv\Scripts\activate #en Windows o en Linux source venv/bin/activate  # 
pip install -r requirements.txt

## Setear el .env con las variables de entorno necesarias

OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

LITELLM_API_KEY_OPENAI=sk-...
LITELLM_API_KEY_DEEPSEEK=sk-...


## Ejecución Local

uvicorn main:app --reload


