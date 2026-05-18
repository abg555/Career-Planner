from openai import OpenAI
from dotenv import load_dotenv
import json
import ast
import os

load_dotenv()

class LLMInterface:
    def __init__(self, api_key=None, model_name="llama-3.1-8b-instant"):     #"llama-3.1-8b-instant"   o  #"llama-3.3-70b-versatile" 
        self.model_name = model_name
        self.api_key = api_key or os.getenv("API_KEY")
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.groq.com/openai/v1")

    def _call_llm(self, prompt, expect_json=False):
        try:
            extra_params = {}
            if expect_json:
                extra_params["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                **extra_params
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error llamando a Groq: {e}")
            return None

    def get_goals_from_text(self, user_text, skills_list):
        prompt = f"""
        Eres un extractor de entidades experto en educación. Tu única tarea es identificar cuáles de las habilidades permitidas en la lista son metas académicas o profesionales del usuario.

        Lista de habilidades permitidas obligatorias: {skills_list}

        GUÍA DE VERBOS - CRÍTICO:
        PRESENTE (ya sabe/experiencia) → NO incluir en goals:
        - "se", "conozco", "tengo experiencia", "domino", "ya", "actualmente", "sé", "manejo"
        
        FUTURO (metas/deseos) → INCLUIR en goals:
        - "quiero", "me interesa", "busco", "deseo", "mi meta", "mi objetivo", "trabajar en", "aprender", "soy principiante en"

        Instrucciones críticas:
        1. Analiza CADA habilidad mencionada INDIVIDUALMENTE.
        2. Si una habilidad aparece con verbos de PRESENTE/EXPERIENCIA (se, conozco, tengo, ya, domino, actualmente), NO la incluyas en goals BAJO NINGUNA CIRCUNSTANCIA.
        3. Si una habilidad aparece SOLO con verbos de FUTURO/METAS, inclúyela en goals.
        4. IMPORTANTE: Si la misma habilidad aparece en ambos contextos (ej: "ya conozco bases de datos pero quiero mejorar"), prioriza el contexto de PRESENTE/EXPERIENCIA y NO la incluyas en goals.
        5. NO deduzcas rutas de aprendizaje. Solo extrae lo que se menciona explícitamente.

        Reglas estrictas de salida:
        - Responde ÚNICAMENTE con un objeto JSON que contenga una lista bajo la llave "goals", ejemplo: {{"goals": ["programador_web"]}}
        - Si no identificas ninguna meta que coincida con la lista permitida, devuelve: {{"goals": []}}
        - No incluyas explicaciones, saludos ni formato Markdown.

        Texto del usuario a analizar:
        "{user_text}"
        """
        response_text = self._call_llm(prompt, expect_json=True)
        if not response_text:
            return []

        try:
            data = json.loads(response_text)
            return data.get("goals", [])
        except Exception as e:
            print(f"Error parseando metas en LLM: {e}. Respuesta cruda: {response_text}")
            return []

    def get_start_skill(self, user_text, skills_list):
        prompt = f"""
        Eres un extractor de entidades experto en educación. Tu única tarea es identificar cuáles de las habilidades permitidas en la lista el usuario YA SABE o CONOCE en el presente.

        Lista de habilidades permitidas obligatorias: {skills_list}

        GUÍA DE VERBOS - CRÍTICO:
        PRESENTE (ya sabe/experiencia) → INCLUIR en start_skills:
        - "se", "conozco", "tengo experiencia", "domino", "ya", "actualmente", "sé", "manejo", "soy experto", "tengo skills"
        
        FUTURO (metas/deseos) → NO incluir:
        - "quiero", "me interesa", "busco", "deseo", "mi meta", "mi objetivo", "trabajar en", "aprender", "soy principiante en"

        Instrucciones críticas:
        1. Analiza CADA habilidad mencionada INDIVIDUALMENTE.
        2. Si una habilidad aparece con verbos de FUTURO/METAS (quiero, me interesa, busco, aprender, etc.), NO la incluyas en start_skills BAJO NINGUNA CIRCUNSTANCIA.
        3. Si una habilidad aparece SOLO con verbos de PRESENTE/EXPERIENCIA, inclúyela en start_skills.
        4. IMPORTANTE: Si la misma habilidad aparece en ambos contextos (ej: "ya conozco bases de datos pero quiero mejorar"), prioriza el contexto de FUTURO/METAS y NO la incluyas en start_skills.
        5. Si el usuario dice "no sé nada", "quiero empezar desde cero" o "soy principiante", significa que su conocimiento es cero.

        Reglas estrictas de salida:
        - Responde ÚNICAMENTE con un objeto JSON que contenga una lista bajo la llave "start_skills", ejemplo: {{"start_skills": ["bases_de_datos"]}}
        - Si no identificas conocimientos actuales, devuelve: {{"start_skills": []}}
        - No incluyas explicaciones ni texto adicional.

        Texto del usuario a analizar:
        "{user_text}"
        """
        response_text = self._call_llm(prompt, expect_json=True)
        if not response_text:
            return []

        try:
            data = json.loads(response_text)
            return data.get("start_skills", [])
        except Exception as e:
            print(f"Error parseando conocimientos en LLM: {e}. Respuesta cruda: {response_text}")
            return []

    def get_money(self, user_text):
        prompt = f"""
        Eres un extractor de presupuesto analítico. Tu tarea es extraer la cantidad de dinero disponible.

        Reglas estrictas:
        1. Responde ÚNICAMENTE con un objeto JSON que contenga el número entero limpio bajo la llave "money", ejemplo: {{"money": 100}}
        2. Si el usuario NO menciona explícitamente ninguna cantidad de dinero, presupuesto o costos, responde exactamente: {{"money": -1}}
        3. No incluyas explicaciones, ni símbolos de moneda.

        Texto del usuario a analizar:
        "{user_text}"
        """
        response_text = self._call_llm(prompt, expect_json=True)
        if not response_text:
            return 10000000000000

        try:
            data = json.loads(response_text)
            num = int(data.get("money", -1))
            return 10000000000000 if num == -1 else num
        except:
            return 10000000000000

    def get_time(self, user_text):
        prompt = f"""
        Eres un extractor de tiempo educativo. Tu tarea es identificar el plazo o duración mencionado por el usuario.

        Reglas estrictas de formato:
        Responde ÚNICAMENTE con un objeto JSON con el formato exacto: {{"time": "[número] [unidad]"}}
        Donde [unidad] puede ser: meses, semanas, dias, anos o horas.
        Ejemplo válido: {{"time": "3 meses"}}
        Si el usuario no menciona plazos de tiempo, responde exactamente: {{"time": "-1"}}

        Texto del usuario a analizar:
        "{user_text}"
        """
        response_text = self._call_llm(prompt, expect_json=True)
        if not response_text:
            return 10000000000000

        try:
            data = json.loads(response_text)
            time_val = data.get("time", "-1").lower()
            if "-1" in time_val:
                return 10000000000000

            parts = time_val.split()
            cantidad = int("".join([c for c in parts[0] if c.isdigit()]))
            unidad = parts[1]

            if "mes" in unidad:
                return cantidad * 30 * 8
            elif "semana" in unidad:
                return cantidad * 7 * 8
            elif "dia" in unidad:
                return cantidad * 8
            elif "ano" in unidad or "año" in unidad:
                return cantidad * 365 * 8
            elif "hora" in unidad:
                return cantidad
            return 10000000000000
        except:
            return 10000000000000

    def get_modality(self, user_text, modalities):
        prompt = f"""
        Eres un extractor de modalidades de estudio experto. Tu tarea es mapear la preferencia del usuario con la lista permitida: {modalities}

        Guía de mapeo semántico obligatorio:
        - Si el usuario dice "presencial", "en persona" o asistir físicamente -> "presencial"
        - Si el usuario dice "online", "virtual", "desde la casa" o por internet -> "online"
        - Si menciona una combinación (ej. "ir presencial pero también quedarme en la casa", "híbrido", o "mitad y mitad") -> "mixto"

        Reglas estrictas:
        1. Responde ÚNICAMENTE con un objeto JSON que contenga la lista bajo la llave "modalities", ejemplo: {{"modalities": ["mixto"]}}
        2. Si el usuario NO menciona ninguna preferencia sobre la modalidad de estudio, responde exactamente: {{"modalities": ["NINGUNA"]}}

        Texto del usuario a analizar:
        "{user_text}"
        """
        response_text = self._call_llm(prompt, expect_json=True)
        if not response_text:
            return modalities

        try:
            data = json.loads(response_text)
            res = data.get("modalities", [])
            if "NINGUNA" in res or not res:
                return modalities
            return res
        except:
            return modalities

    def get_difficulty(self, user_text, difficulties):
        prompt = f"""
        Eres un extractor de texto experto en análisis de restricciones sobre dificultad académica.

        ANÁLISIS CRÍTICO - 3 Escenarios:

        ESCENARIO 1 - MENCIÓN EXPLÍCITA de dificultad:
        - Usuario menciona palabras como: "baja", "media", "alta", "avanzado", "básico", "intermedio", "difícil", "fácil"
        - ACCIÓN: Extrae la dificultad mencionada (mapea "avanzado"→"alta")
        - EJEMPLO: "quiero cursos de dificultad alta" → {{"difficulties": ["alta"]}}

        ESCENARIO 2 - NEGACIÓN EXPLÍCITA de dificultad:
        - Usuario dice: "NO quiero cursos de alta dificultad", "no quiero avanzado", "evita lo difícil", etc.
        - ACCIÓN: Retorna las dificultades que SÍ aceptaría (excluye la rechazada)
        - EJEMPLO: "no quiero cursos de alta dificultad" → {{"difficulties": ["baja", "media"]}}

        ESCENARIO 3 - SIN MENCIÓN DE DIFICULTAD (ni explícita ni negación):
        - Usuario NO menciona nada sobre dificultad del curso
        - ACCIÓN: Retorna "NINGUNA" (el sistema debe ofrecerle todas las opciones)
        - EJEMPLO: "Me interesa desarrollo web pero ya conozco bases de datos" → {{"difficulties": ["NINGUNA"]}}

        EXCEPCIÓN ESPECIAL - NIVEL DEL USUARIO (no es preferencia de dificultad del curso):
        - Si usuario dice "soy principiante", "no sé nada", "sin experiencia" → IGNORA. No es preferencia de dificultad del curso.
        - Si usuario dice "soy experto", "tengo experiencia" → IGNORA. No es preferencia de dificultad del curso.
        - Estas son autoevaluaciones, NO preferencias sobre cursos. Retorna "NINGUNA" igual.

        Reglas estrictas:
        1. Responde ÚNICAMENTE con un objeto JSON bajo la llave "difficulties"
        2. Si NO hay mención explícita de dificultad (ni positiva ni negativa), retorna: {{"difficulties": ["NINGUNA"]}}
        3. Si hay negación, retorna lista sin lo rechazado: {{"difficulties": ["baja", "media"]}}
        4. Si hay mención positiva, retorna: {{"difficulties": ["alta"]}}

        Texto del usuario a analizar:
        "{user_text}"
        """
        response_text = self._call_llm(prompt, expect_json=True)
        if not response_text:
            return difficulties

        try:
            data = json.loads(response_text)
            res = data.get("difficulties", [])
            if "NINGUNA" in res or not res:
                return difficulties
            return res
        except:
            return difficulties

    