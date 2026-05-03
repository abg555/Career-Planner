from google import genai
import json
import time
import ast

class LLMInterface:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash"

    def get_goals_from_text(self, user_text, skills_list):
        prompt = f"""
        Eres un extractor de entidades experto en educación.
        Tu tarea es identificar cuáles de estas habilidades: {skills_list}
        quiere aprender el usuario basándote en su mensaje: "{user_text}".
        Reglas estrictas:
        1. Responde ÚNICAMENTE con una lista (usa comillas dobles).
        2. Si no identificas ninguna, responde: [].
        3. No incluyas explicaciones ni texto adicional.
        """

        models_to_try = [
            "models/gemini-2.5-flash",      
            "models/gemini-2.0-flash",       
            "models/gemini-2.0-flash-lite"  
        ]

        for model in models_to_try:
            for attempt in range(3):
                try:
                    response = self.client.models.generate_content(model=model,contents=prompt)
                    text_response = response.text.strip()

                    if "```" in text_response:
                        text_response = text_response.split("```")[1]
                        text_response = text_response.replace("json", "").replace("python", "").strip()

                    return ast.literal_eval(text_response)

                except Exception as e:
                    print(f"[{model}] intento {attempt+1} falló: {e}")
                    time.sleep(1.5 * (attempt + 1))  # backoff

        return []

    def explain_plan(self, plan_ids, courses_data):
        relevant_info = [course for course in courses_data if course['id'] in plan_ids]

        prompt = f"""
        Has generado un plan de estudios para un estudiante. 
        Los cursos elegidos son: {relevant_info}.
        Explica brevemente al usuario por qué este camino es el ideal para alcanzar sus metas. 
        Mantén un tono motivador y profesional.
        """

        models_to_try = [
            "models/gemini-2.5-flash",
            "models/gemini-2.0-flash",
            "models/gemini-2.0-flash-lite"
        ]

        for model in models_to_try:
            for attempt in range(3):
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt
                    )
                    return response.text.strip()

                except Exception as e:
                    print(f"[EXPLAIN {model}] intento {attempt+1} falló: {e}")
                    time.sleep(1.5 * (attempt + 1))

        return f"\n[Aviso: No se pudo generar la explicación, pero aquí tienes tu ruta técnica]: {', '.join(plan_ids)}"