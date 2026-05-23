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
        6. Si el usuario dice expresiones de conocimiento parcial pero explícito como "sé algo de X", "tengo algo de X", "conozco un poco de X" o "manejo X a nivel básico", INCLÚYE la habilidad X en start_skills.
        7. Si el usuario menciona una habilidad con la palabra "básica" junto a una expresión de conocimiento actual (por ejemplo: "sé algo de programación básica"), considérala como conocimiento actual y extráela en start_skills.
        8. Ejemplo CRÍTICO: si el texto dice "me gustaría aprender backend ... pero sé algo de programación básica", debes devolver start_skills con ["programacion_basica"] aunque el resto del texto hable de metas futuras.
        9. No confundas deseos de aprendizaje con conocimiento actual: si una habilidad aparece con una señal clara de presente (se algo de / tengo algo de / conozco un poco de), esa habilidad debe ir en start_skills aunque en la misma frase haya palabras como "quiero" o "me gustaría" referidas a otras habilidades.

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
        Si el texto contiene una duración explícita dentro de una frase larga (por ejemplo: "cuento con 3 semanas", "tengo 90 dias", "dispongo de 2 meses"), debes extraer ESA duración exacta y no responder -1.
        Si hay más de una referencia de tiempo, elige la primera duración explícita que describa disponibilidad del usuario.

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
                - Si menciona una combinación explícita (ej. "híbrido", "mitad y mitad", "presencial y online") -> "mixto"
                - Si dice "puedo" o "puedes" seguido de lista de modalidades (ej. "puedo estudiar online, mixto o presencial") -> devuelve TODAS esas modalidades.
                - Si usa exclusividad como "solo", "únicamente", "solamente" con una modalidad, devuelve SOLO esa modalidad.
                    Ejemplos: "solo online" -> ["online"], "solo presencial" -> ["presencial"].
                - Si rechaza explícitamente una modalidad, devuelve las modalidades compatibles que no estén rechazadas.
                    Ejemplo: "no me gustan los cursos presenciales" -> ["online", "mixto"] si esas opciones existen en la lista permitida.
                - Si el usuario dice que no quiere presencial pero tampoco pide mixto, devuelve igualmente ["online", "mixto"] salvo que rechace explícitamente "mixto".
                - Si el usuario rechaza presencial, asume que también acepta mixta si no la prohíbe de forma directa.

        Reglas estrictas:
        1. Responde ÚNICAMENTE con un objeto JSON que contenga la lista bajo la llave "modalities", ejemplo: {{"modalities": ["online", "mixto", "presencial"]}}
                1.1 Si el usuario menciona "puedo estudiar X, Y, Z" devuelve TODAS esas modalidades en la lista.
                1.2 Si hay negación de una modalidad, la lista puede contener MÁS DE UNA opción compatible.
                1.3 Si el usuario pide una sola modalidad con exclusividad, NO agregues otras modalidades.
        2. Si el usuario NO menciona ninguna preferencia sobre la modalidad de estudio, responde exactamente: {{"modalities": ["NINGUNA"]}}
        3. Si el usuario menciona una preferencia positiva explícita y además niega otra, devuelve la lista completa de compatibles.
        4. No inventes modalidades que el usuario no sugirió, excepto cuando la negación de presencial implique también mixto como opción compatible.
        5. Si el texto solo dice "online" o "presencial" sin negaciones, devuelve exactamente esa modalidad.

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

            normalized_text = str(user_text).lower()
            rejects_presential = any(phrase in normalized_text for phrase in [
                "no me gustan los cursos presenciales",
                "no me gusta la modalidad presencial",
                "no presencial",
                "evita presencial",
                "sin presencial",
                "no quiero presencial",
                "rechazo presencial",
            ])
            mentions_mixed = any(phrase in normalized_text for phrase in [
                "mixto", "hibrido", "híbrido", "mitad y mitad", "presencial y online"
            ])
            explicit_online = any(phrase in normalized_text for phrase in [
                "solo online", "únicamente online", "unicamente online", "solo virtual", "solo por internet"
            ])
            explicit_only_presential = any(phrase in normalized_text for phrase in [
                "solo presencial", "únicamente presencial", "unicamente presencial"
            ])
            
            can_study = any(phrase in normalized_text for phrase in [
                "puedo estudiar", "puedes estudiar", "acepto", "acepté", "aceptamos"
            ])
            has_list_markers = " o " in normalized_text or "," in normalized_text

            if explicit_only_presential:
                return ["presencial"] if "presencial" in modalities else modalities

            if rejects_presential and not mentions_mixed and not explicit_online:
                final_res = []
                if "online" in modalities:
                    final_res.append("online")
                if "mixto" in modalities:
                    final_res.append("mixto")
                if final_res:
                    return final_res

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

    def compare_and_evaluate_trajectories(self, user_text, trajectories_dict):
        """
        Compara múltiples trayectorias generadas por diferentes algoritmos de búsqueda,
        las evalúa bajo restricciones cualitativas y resume sus ventajas, desventajas
        y la conclusión más alineada con lo que busca el usuario.
        
        :param user_text: Entrada original del usuario (metas, tiempo, dinero, modalidad).
        :param trajectories_dict: Diccionario donde la clave es el nombre del algoritmo 
                                  y el valor es la lista de cursos de esa trayectoria.
        """
        cleaned_payload = {}
        route_summaries = {}
        route_ids_map = {}  
        
        for algo_name, courses_list in trajectories_dict.items():
            cleaned_payload[algo_name] = []
            total_cost = 0
            total_time = 0
            course_ids = []
            for course in courses_list:
                course_cost = int(course.get("cost", 0) or 0)
                course_time = int(course.get("duration_hours", 0) or 0)
                total_cost += course_cost
                total_time += course_time
                course_ids.append(course.get("id"))
                cleaned_payload[algo_name].append({
                    "id": course.get("id"),
                    "title": course.get("title"),
                    "description": course.get("description", ""),
                    "prerequisites": course.get("prerequisites", []),
                    "effects": course.get("effects", []),
                    "cost": course_cost,
                    "duration_hours": course_time,
                    "modality": course.get("modality"),
                    "difficulty": course.get("difficulty")
                })

            route_summaries[algo_name] = {
                "courses": len(courses_list),
                "course_ids": course_ids,
                "total_cost": total_cost,
                "total_time": total_time,
            }
            
            course_ids_tuple = tuple(course_ids)
            if course_ids_tuple not in route_ids_map:
                route_ids_map[course_ids_tuple] = []
            route_ids_map[course_ids_tuple].append(algo_name)

        duplicates_info = {}
        for course_ids_tuple, algo_names in route_ids_map.items():
            if len(algo_names) > 1:
                primary = algo_names[0]
                for dup_name in algo_names[1:]:
                    duplicates_info[dup_name] = primary

        route_summary_text = json.dumps(route_summaries, ensure_ascii=False, indent=2)
        duplicates_text = ""
        if duplicates_info:
            duplicates_text = "\n\nRUTAS IDÉNTICAS DETECTADAS:\n"
            for dup_name, primary_name in duplicates_info.items():
                duplicates_text += f"- {dup_name} aporta exactamente lo mismo que {primary_name} (mismos cursos, misma secuencia).\n"

        prompt = f"""
        Eres un auditor académico de nivel doctoral y experto en diseño curricular de sistemas informáticos e Inteligencia Artificial.
        Tu tarea es realizar un análisis comparativo riguroso de múltiples trayectorias alternativas sugeridas por diferentes algoritmos de búsqueda para un estudiante.

        REQUISITOS Y RESTRICCIONES REALES DEL USUARIO:
        "{user_text}"

        TRAYECTORIAS CANDIDATAS DISPONIBLES:
        {json.dumps(cleaned_payload, ensure_ascii=False, indent=2)}

        RESUMEN EXACTO DE CADA RUTA (usa estos números sin cambiarlos):
        {route_summary_text}{duplicates_text}

        INSTRUCCIONES METODOLÓGICAS PARA TU ANÁLISIS:
        1. USA SOLAMENTE LOS NÚMEROS DEL "RESUMEN EXACTO DE CADA RUTA" para costo, tiempo y número de cursos.
        2. NO INVENTES cifras. Si dices que una ruta es la más barata o la más rápida, debe coincidir exactamente con el resumen.
        3. DENSIDAD PEDAGÓGICA Y TRANSICIÓN: Evalúa la curva de aprendizaje. Pasar de una dificultad 'baja' a 'alta' de forma abrupta es un punto negativo.
        4. CONSISTENCIA DE OBJETIVOS: Explica qué ruta cubre mejor los objetivos del usuario con base en sus efectos reales.
        5. SIN LENGUAJE DE COMPETENCIA: No hables de "ganadores", "perdedores" o "derrotas". Enfoca el análisis en trade-offs claros.
        6. Si una ruta tiene menos costo total que otra, no la llames más costosa.
        7. Si una ruta tiene menos tiempo total que otra, no la digas más lenta.
        8. La conclusión final no debe centrarse solo en costo/tiempo: también debe mencionar cobertura de objetivos, progresión pedagógica, prerrequisitos y modalidad cuando aporten al análisis.
        9. Si una ruta es mejor en costo/tiempo pero peor en cobertura pedagógica, dilo explícitamente como un trade-off.
        10. SI HAY RUTAS IDÉNTICAS: Incluye una nota en los pros o cons de la ruta duplicada diciendo "Esta ruta aporta exactamente lo mismo que [Nombre de ruta original]" o similar.

        Reglas estrictas de salida:
        Responde ÚNICAMENTE con un objeto JSON perfectamente estructurado de esta forma, sin bloques markdown:
        {{
            "final_conclusion": "Un desglose analítico detallado que explique de forma clara los trade-offs económicos y pedagógicos entre las opciones, concluyendo cuál es el balance ideal para el perfil específico del usuario.",
            "ranking": [
                {{
                    "name": "[Nombre exacto de la trayectoria, ej: 'Ruta UCS (Costo)']",
                    "score": [Número entero de 1 a 100],
                    "pros": [
                        "Ventaja específica basada en datos reales (ej: 'Es la opción más barata con un costo total de $28')",
                        "Ventaja cualitativa/pedagógica (ej: 'Mantiene una transición de dificultad baja a media ideal para principiantes')"
                    ],
                    "cons": [
                        "Desventaja específica (ej: 'El curso 'ia_completa_2meses' presenta un salto brusco a dificultad alta')",
                        "Desventaja de recursos (ej: 'Consume 218 horas, acercándose considerablemente al límite del usuario')"
                    ]
                }}
            ],
            "recommended_trajectory_name": "[Nombre exacto de la trayectoria que ofrece el mejor equilibrio para el usuario]"
        }}

        IMPORTANTE: 
        - Sé sumamente específico. Si mencionas costo o tiempo, escribe los valores exactos del resumen.
        - La conclusión final debe comparar explícitamente al menos dos trayectorias con base en sus métricas reales y en su valor pedagógico.
        - La conclusión debe sonar equilibrada: por ejemplo, explicar que una ruta es más económica pero otra cubre mejor los objetivos o tiene una progresión más adecuada.
        - Todas las trayectorias provistas son válidas a nivel de grafos; concéntrate en la experiencia educativa y la optimización de recursos.
        - Si dos rutas son idénticas, menciona explícitamente cuál es el duplicado en el ranking.
        """

        response_text = self._call_llm(prompt, expect_json=True)
        if not response_text:
            return {
                "final_conclusion": "No se pudo obtener respuesta del LLM debido a un error de comunicación.",
                "ranking": [],
                "recommended_trajectory_name": "No determinado"
            }

        try:
            cleaned_text = response_text
            if cleaned_text.startswith("```"):
                lines = cleaned_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned_text = "\n".join(lines).strip()

            data = json.loads(cleaned_text)
            
            if "final_conclusion" not in data:
                data["final_conclusion"] = data.get("justification", data.get("conclusion_final", "Sin conclusión disponible."))
            if "recommended_trajectory_name" not in data:
                data["recommended_trajectory_name"] = data.get("best_trajectory_name", "No determinado")
                
            return data
        except Exception as e:
            print(f"Error parseando la comparación del LLM: {e}. Respuesta cruda: {response_text}")
            return {
                "final_conclusion": "Error al procesar el formato estructurado del análisis comparativo.",
                "ranking": [],
                "recommended_trajectory_name": "Error de parsing"
            }
        
    def evaluate_adaptive_trajectory(self, user_text, adaptive_trajectory, all_modalities, all_difficulties):
        """
        Evalúa una trayectoria generada por el Adaptive Planner y la compara con el texto original del usuario.
        Si la ruta difiere de las expectativas, explica qué restricciones fueron relajadas y por qué.
        
        :param user_text: Texto original del usuario con sus metas y restricciones.
        :param adaptive_trajectory: Lista de diccionarios de cursos de la ruta adaptativa.
        :param all_modalities: Lista de modalidades disponibles en el dataset.
        :param all_difficulties: Lista de dificultades disponibles en el dataset.
        :return: Diccionario con análisis de diferencias y justificación.
        """
        goal_skills = self.get_goals_from_text(user_text, []) 
        modalities_requested = self.get_modality(user_text, all_modalities)
        difficulties_requested = self.get_difficulty(user_text, all_difficulties)
        money_requested = self.get_money(user_text)
        time_requested = self.get_time(user_text)

       
        route_skills = set()
        route_modalities = set()
        route_difficulties = set()
        total_cost = 0
        total_time = 0

        for course in adaptive_trajectory:
            route_modalities.add(course.get("modality", "desconocida"))
            route_difficulties.add(course.get("difficulty", "desconocida"))
            total_cost += int(course.get("cost", 0) or 0)
            total_time += int(course.get("duration_hours", 0) or 0)
        
            for effect in course.get("effects", []):
                route_skills.add(effect)

        route_payload = []
        for course in adaptive_trajectory:
            route_payload.append({
                "id": course.get("id"),
                "title": course.get("title"),
                "modality": course.get("modality"),
                "difficulty": course.get("difficulty"),
                "cost": int(course.get("cost", 0) or 0),
                "duration_hours": int(course.get("duration_hours", 0) or 0),
                "effects": course.get("effects", [])
            })

        prompt = f"""
        Eres un consejero académico experto. El usuario solicitó lo siguiente:
        
        SOLICITUD DEL USUARIO:
        "{user_text}"
        
        El sistema no encontró una ruta que cumpla EXACTAMENTE con todas las restricciones, 
        por lo que el Adaptive Planner propone esta ruta alternativa:
        
        RUTA ADAPTATIVA PROPUESTA:
        {json.dumps(route_payload, ensure_ascii=False, indent=2)}
        
        RESUMEN NUMÉRICO:
        - Número de cursos: {len(adaptive_trajectory)}
        - Costo total: ${total_cost}
        - Tiempo total: {total_time} horas
        - Modalidades en la ruta: {', '.join(route_modalities)}
        - Dificultades en la ruta: {', '.join(route_difficulties)}
        - Skills enseñados: {', '.join(route_skills)}
        
        RESTRICCIONES SOLICITADAS POR EL USUARIO:
        - Modalidades aceptadas: {', '.join(modalities_requested) if modalities_requested else 'Cualquiera'}
        - Dificultades aceptadas: {', '.join(difficulties_requested) if difficulties_requested else 'Cualquiera'}
        - Presupuesto máximo: ${money_requested if money_requested != 10000000000000 else 'Sin límite'}
        - Tiempo máximo: {time_requested if time_requested != 10000000000000 else 'Sin límite'} horas
        
        Tu tarea es:
        1. Identificar qué restricciones fue necesario relajar para encontrar esta ruta.
        2. Explicar de forma clara y empática por qué se necesitó relajar cada restricción.
        3. Destacar los aspectos positivos de esta ruta alternativa.
        4. Proporcionar una justificación pedagógica de por qué esta ruta sigue siendo valiosa.
        
        Responde ÚNICAMENTE con un JSON así:
        {{
            "restricciones_relajadas": [
                {{
                    "restriccion": "[nombre de restricción, ej: 'Modalidad', 'Dificultad', 'Tiempo', 'Dinero']",
                    "solicitado": "[Lo que solicitó el usuario, ej: 'Solo presencial']",
                    "ofrecido": "[Lo que la ruta ofrece, ej: 'Online y mixto']",
                    "razon": "[Explicación breve de por qué no hay otras opciones]"
                }}
            ],
            "aspectos_positivos": [
                "Ventaja específica (ej: 'Cubre todas las metas de aprendizaje en solo 180 horas')",
                "Otra ventaja..."
            ],
            "justificacion_general": "Un párrafo que explique por qué esta ruta sigue siendo una buena opción pedagógica a pesar de las diferencias."
        }}
        """

        response_text = self._call_llm(prompt, expect_json=True)
        if not response_text:
            return {
                "restricciones_relajadas": [],
                "aspectos_positivos": [],
                "justificacion_general": "No se pudo obtener análisis del LLM."
            }

        try:
            cleaned_text = response_text
            if cleaned_text.startswith("```"):
                lines = cleaned_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned_text = "\n".join(lines).strip()

            data = json.loads(cleaned_text)
            return data
        except Exception as e:
            print(f"Error parseando evaluación adaptativa: {e}")
            return {
                "restricciones_relajadas": [],
                "aspectos_positivos": [],
                "justificacion_general": f"Error al procesar el análisis. Detalles: {str(e)}"
            }