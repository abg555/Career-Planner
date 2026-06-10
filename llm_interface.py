from openai import OpenAI
from dotenv import load_dotenv
import json
import ast
import os

    
load_dotenv()

class LLMInterface:
    def __init__(self, api_key=None, model_name="llama-3.3-70b-versatile"):     #"llama-3.1-8b-instant"   o  #"llama-3.3-70b-versatile" 
        self.model_name = model_name                      #modelo
        self.api_key = api_key or os.getenv("API_KEY")    #api key
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.groq.com/openai/v1")          #cliente Groq

    def _call_llm(self, prompt, expect_json=False):     #Método privado que encapsula las llamadas directas a la API de Groq
        try:
            extra_params = {}
            if expect_json:        # Activa el modo JSON a nivel de API
                extra_params["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,        #Temperatura baja para asegurar consistencia y determinismo en las extracciones
                **extra_params
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error llamando a Groq: {e}")
            return None

    def get_goals_from_text(self, user_text, skills_list):      #Analiza la consulta en lenguaje natural para extraer los objetivos
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
            data = json.loads(response_text)          # Convierte la respuesta en un diccionario y extrae la lista de metas
            return data.get("goals", [])
        except Exception as e:
            print(f"Error parseando metas en LLM: {e}. Respuesta cruda: {response_text}")
            return []

    def get_start_skill(self, user_text, skills_list):        #Interpreta el texto para identificar las habilidades actuales
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
            data = json.loads(response_text)         # Convierte la respuesta en un diccionario y extrae la lista de metas
            return data.get("start_skills", [])
        except Exception as e:
            print(f"Error parseando conocimientos en LLM: {e}. Respuesta cruda: {response_text}")
            return []

    def get_money(self, user_text):         #Extrae el presupuesto financiero límite introducido por el usuario
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
        if not response_text:      # Si falla la llamada, asume un presupuesto infinito virtual para no bloquear las búsquedas
            return 10000000000000

        try:
            data = json.loads(response_text)     # Si retorna -1 indica sin restricciones; se reemplaza por el presupuesto infinito
            num = int(data.get("money", -1))
            return 10000000000000 if num == -1 else num
        except:
            return 10000000000000

    def get_time(self, user_text):         #Extrae la restricción temporal descrita en la consulta, y la normaliza a horas estimadas
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

            if "mes" in unidad:    # Lógica de Parseo y Conversión a Horas, se asume 8 horas diarias de jornada academica, cada mes con 30 dias y cada ano con 365 dias
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

    def get_modality(self, user_text, modalities):    #Interpreta semánticamente las preferencias sobre la modalidad de estudio
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

            normalized_text = str(user_text).lower()    # Lógica secundaria para mitigar oraciones de rechazo ambiguas
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

    def get_difficulty(self, user_text, difficulties):    #Identifica si el usuario exige un nivel de dificultad específico en las asignaturas o si se descartan niveles de forma explícita
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
            if "NINGUNA" in res or not res:   # Si no hay filtros directos, se asume que se aceptan todas las dificultades cargadas
                return difficulties
            return res
        except:
            return difficulties

    def compare_and_evaluate_trajectories(self, user_text, trajectories_dict):     #Compara múltiples trayectorias generadas por los diferentes algoritmos de búsqueda (BFS, UCS, A*)
        """
        Compara múltiples trayectorias generadas por diferentes algoritmos de búsqueda,
        realizando un análisis cualitativo, cruzado y discursivo detallado basado 
        estrictamente en sus datos reales (costo, tiempo, volumen y progresión pedagógica),
        calculando previamente las verdades matemáticas para evitar alucinaciones relativas.
        """
        cleaned_payload = {}
        route_summaries = {}
        route_ids_map = {}  
        
        #Extracción de métricas base y construcción del payload limpio
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

            route_summaries[algo_name] = {      # Estructura el resumen estadístico real para dárselo procesado al LLM
                "courses": len(courses_list),
                "course_ids": course_ids,
                "total_cost": total_cost,
                "total_time": total_time,
            }
            
            course_ids_tuple = tuple(course_ids)     # Identifica equivalencias en las soluciones para la lógica de agrupación dinámica
            if course_ids_tuple not in route_ids_map:
                route_ids_map[course_ids_tuple] = []
            route_ids_map[course_ids_tuple].append(algo_name)

        if not route_summaries:
            return {
                "analisis_detallado_alternativas": "No se encontraron trayectorias válidas generadas por los algoritmos para auditar.",
                "guia_orientacion_usuario": "Por favor, intente con otra consulta."
            }

        # detección e informe de rutas idénticas
        duplicates_info = {}
        for course_ids_tuple, algo_names in route_ids_map.items():
            if len(algo_names) > 1:
                primary = algo_names[0]
                for dup_name in algo_names[1:]:
                    duplicates_info[dup_name] = primary

        route_summary_text = ""
        for algo, metrics in route_summaries.items():
            route_summary_text += f"- {algo}: Costo Total = ${metrics['total_cost']}, Tiempo Total = {metrics['total_time']} horas, Cantidad de Cursos = {metrics['courses']}.\n"

        duplicates_text = ""
        if duplicates_info:
            duplicates_text = "\n\nRUTAS IDÉNTICAS DETECTADAS:\n"
            for dup_name, primary_name in duplicates_info.items():
                duplicates_text += f"- {dup_name} aporta exactamente lo mismo que {primary_name} (mismos cursos, misma secuencia).\n"

        #preporcesamiento de verdad matematica, (previene alucionaciones del LLM)
        try:
            metrica_tiempo = {k: v["total_time"] for k, v in route_summaries.items()}
            metrica_costo = {k: v["total_cost"] for k, v in route_summaries.items()}
            metrica_cursos = {k: v["courses"] for k, v in route_summaries.items()}
            
            mas_rapido_algo = min(metrica_tiempo, key=metrica_tiempo.get) # Cálculos de extremos numéricos absolutos
            mas_lento_algo = max(metrica_tiempo, key=metrica_tiempo.get)
            mas_barato_algo = min(metrica_costo, key=metrica_costo.get)
            mas_caro_algo = max(metrica_costo, key=metrica_costo.get)
            menos_cursos_algo = min(metrica_cursos, key=metrica_cursos.get)
            mas_cursos_algo = max(metrica_cursos, key=metrica_cursos.get)
        except Exception as e:
            print(f"[Error en Preprocesamiento Numérico]: {e}")
            mas_rapido_algo = mas_lento_algo = mas_barato_algo = mas_caro_algo = "N/A"
            menos_cursos_algo = mas_cursos_algo = "N/A"

        # Mapear las secuencias explícitas de dificultad para dárselas procesadas
        secuencias_dificultad_texto = ""
        for algo, cursos in cleaned_payload.items():
            dif_list = [str(c.get('difficulty', 'Baja')).capitalize() for c in cursos]
            if dif_list:
                secuencias_dificultad_texto += f"- Secuencia real de dificultad para {algo}: {' -> '.join(dif_list)}\n"

        # Bloque inyectable con las verdades absolutas comparativas
        verdades_numericas_computadas = f"""
        VERDADES MATEMÁTICAS CALCULADAS POR EL SISTEMA (PROHIBIDO TOTALMENTE CONTRADECIR ESTOS DATOS RELATIVOS):
        - La ruta MÁS RÁPIDA (menos horas totales acumuladas) es estrictamente: {mas_rapido_algo} ({metrica_tiempo.get(mas_rapido_algo, 0)} horas).
        - La ruta MÁS LENTA (más horas totales acumuladas) es estrictamente: {mas_lento_algo} ({metrica_tiempo.get(mas_lento_algo, 0)} horas).
        - La ruta MÁS BARATA (menor costo monetario acumulado) es estrictamente: {mas_barato_algo} (${metrica_costo.get(mas_barato_algo, 0)} USD).
        - La ruta MÁS CARA (mayor costo monetario acumulado) es estrictamente: {mas_caro_algo} (${metrica_costo.get(mas_caro_algo, 0)} USD).
        - La ruta con MENOS CURSOS TOTALES (trayectoria más corta en pasos/trámites) es: {menos_cursos_algo} ({metrica_cursos.get(menos_cursos_algo, 0)} cursos).
        - La ruta con MÁS CURSOS TOTALES (trayectoria formativa más fragmentada) es: {mas_cursos_algo} ({metrica_cursos.get(mas_cursos_algo, 0)} cursos).
        
        SECUENCIAS REALES DE PASOS ACADÉMICOS:
        {secuencias_dificultad_texto}
        """
        #Diseno del prompt
        prompt = f"""
        Eres un asesor académico de nivel doctoral en diseño curricular y un experto en la optimización de trayectorias formativas. Tu tarea es realizar un análisis comparativo cruzado y crítico de las trayectorias sugeridas por los algoritmos de búsqueda basándote ESTRICTAMENTE en los datos de entrada provistos.

        REQUISITOS Y RESTRICCIONES REALES DEL USUARIO:
        "{user_text}"

        TRAYECTORIAS CANDIDATAS DISPONIBLES (Analiza los datos crudos de este JSON):
        {json.dumps(cleaned_payload, ensure_ascii=False, indent=2)}

        RESUMEN DE MÉTRICAS GLOBALES REALES:
        {route_summary_text}{duplicates_text}

        {verdades_numericas_computadas}

        METODOLOGÍA DE AUDITORÍA CRÍTICA COMPLETA:
        1. INSPECCIÓN DETALLADA Y VERACIDAD LOGICIAL: Está TERMINANTEMENTE PROHIBIDO alterar las relaciones de mayor o menor. Si el sistema calculó que una ruta es la de menos horas, es la más rápida, sin importar qué algoritmo sea. Valida cada adjetivo contrastándolo con las 'VERDADES MATEMÁTICAS CALCULADAS POR EL SISTEMA'.
        2. ANÁLISIS DE EFICIENCIA Y CRUCES DE PROPORCIÓN (OBLIGATORIO): Debes contrastar las rutas entre sí evaluando las siguientes métricas cruzadas:
           - PROPORCIÓN TIEMPO/DINERO (Costo-Eficiencia): Analiza cuál trayectoria ofrece el mayor valor educativo por unidad monetaria o temporal invertida. Si un plan destruye el trade-off clásico siendo sumamente económico y rápido al mismo tiempo, acláralo explícitamente como la ruta de máxima eficiencia.
           - DENSIDAD HORARIA POR CURSO: Analiza la relación entre cantidad de cursos y horas totales. Contrasta si un plan de pocos cursos ofrece asignaturas masivas y densas (provocando un potencial cuello de botella de tiempo o fatiga mental), o si una ruta con más cursos ofrece cápsulas más cortas, ágiles y fragmentadas.
        3. AUDITORÍA SECTORIAL DE LA DIFICULTAD PEDAGÓGICA: Observa las secuencias inyectadas:
           - Si una secuencia pasa directamente de 'Baja' a 'Alta' sin pisar el escalón 'Media', descríbelo explícitamente en el párrafo como un 'Salto abrupto y crítico de dificultad (Brecha pedagógica)'.
           - Si la secuencia progresa incluyendo el escalón intermedio ('Baja -> Media -> Alta'), descríbelo como una 'Curva de aprendizaje balanceada y progresiva'.
        4. ANÁLISIS DE CONTENIDO: Examina los títulos y temas para validar si cubren las necesidades específicas planteadas o si desvían el foco académico.
        5. ORIGINALIDAD Y PROHIBICIÓN DE COPIAR TEXTOS: Prohibido usar las mismas estructuras de oraciones para describir alternativas. Cada párrafo debe reflejar dinámicamente la personalidad única de sus datos.

        Reglas estrictas de salida:
        Responde ÚNICAMENTE con un objeto JSON estructurado exactamente con las siguientes dos llaves de texto plano, sin bloques de código markdown:
        {{
            "analisis_detallado_alternativas": "Analiza minuciosamente cada ruta aplicando la metodología paso a paso, integrando de forma obligatoria los contrastes globales de proporción tiempo/dinero y densidad por curso frente a las otras opciones. IMPORTANTE: Usa etiquetas HTML para estructurar. Separa cada ruta iniciando con un título en negrita como '<b>• Ruta [Nombre del Algoritmo]:</b><br>', destaca las métricas críticas, proporciones y hallazgos en negrita (ej: '<b>$150</b>', '<b>máxima eficiencia financiera</b>', '<b>densidad horaria por curso</b>', '<b>salto abrupto de dificultad</b>') y pon obligatoriamente saltos de línea '<br><br>' al finalizar la evaluación de cada trayectoria de forma que queden perfectamente separadas.",
            "guia_orientacion_usuario": "Escribe aquí recomendaciones de decisión personalizadas evaluando los escenarios reales de trade-off y las proporciones optimizadas que se demostraron en las verdades matemáticas. IMPORTANTE: Usa viñetas HTML, por ejemplo:<br><ul><li><b>Si tu prioridad es la mejor proporción tiempo/dinero (Costo-Eficiencia):</b> Te conviene la ruta... porque según los datos...</li><li><b>Si prefieres cursos más cortos, menos densos y fragmentados:</b> Tu opción recomendada es... debido a que ofrece...</li></ul>"
        }}
        """

        # Inferencia a la API garantizando el formato JSON
        response_text = self._call_llm(prompt, expect_json=True)
        if not response_text:
            return {
                "analisis_detallado_alternativas": "No se pudo obtener respuesta del LLM debido a un error de comunicación.",
                "guia_orientacion_usuario": "Por favor, intente la búsqueda nuevamente."
            }

        try:
            cleaned_text = response_text.strip()
            
            import re
            match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if match:
                cleaned_text = match.group(0)

            data = json.loads(cleaned_text)
            return data

        except Exception as e:
            print(f"Error parseando la comparación cualitativa del LLM: {e}. Respuesta cruda: {response_text}")
            return {
                "analisis_detallado_alternativas": f"Error de formato al procesar el análisis estructural.\nRespuesta original:\n{response_text}",
                "guia_orientacion_usuario": "No se pudo descodificar la guía de decisiones por un error de formato JSON."
            }
        
    def evaluate_adaptive_trajectory(self, user_text, adaptive_trajectory, all_modalities, all_difficulties):  #""Audita y justifica cualitativamente el plan generado por el Motor Adaptativo
        """
        Evalúa una trayectoria generada por el Adaptive Planner y la compara con el texto original del usuario.
        Si la ruta difiere de las expectativas, explica qué restricciones fueron relajadas y por qué.
        
        :param user_text: Texto original del usuario con sus metas y restricciones.
        :param adaptive_trajectory: Lista de diccionarios de cursos de la ruta adaptativa.
        :param all_modalities: Lista de modalidades disponibles en el dataset.
        :param all_difficulties: Lista de dificultades disponibles en el dataset.
        :return: Diccionario con análisis de diferencias y justificación.
        """
        goal_skills = self.get_goals_from_text(user_text, [])  # Extrae las restricciones deseadas originales relanzando los métodos de parseo numérico
        modalities_requested = self.get_modality(user_text, all_modalities)
        difficulties_requested = self.get_difficulty(user_text, all_difficulties)
        money_requested = self.get_money(user_text)
        time_requested = self.get_time(user_text)

        route_skills = set()
        route_modalities = set()
        route_difficulties = set()
        total_cost = 0
        total_time = 0

        for course in adaptive_trajectory:    # Computa las métricas de la trayectoria adaptativa real propuesta
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

       # Construcción del prompt evaluativo para el Asesor Académico de la ruta adaptativa
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
        1. Identificar qué restricciones fue necesario relajar para encontrar esta ruta y explicar de forma clara y empática por qué se necesitó relajar en la sección correspondiente.
        2. Redactar una explicación pedagógica general en forma de PÁRRAFO FLUIDO Y CONTINUO. Este párrafo debe integrar obligatoriamente tanto los aspectos positivos y ventajas de esta ruta alternativa como la justificación de por qué sigue siendo una opción excelente para el estudiante. NO uses listas, viñetas, plecas ni guiones en este párrafo.
        
        Responde ÚNICAMENTE con un JSON con la siguiente estructura:
        {{
            "restricciones_relajadas": [
                {{
                    "restriccion": "[nombre de restricción, ej: 'Modalidad', 'Dificultad', 'Tiempo', 'Dinero']",
                    "solicitado": "[Lo que solicitó el usuario, ej: 'Solo presencial']",
                    "ofrecido": "[Lo que la ruta ofrece, ej: 'Online y mixto']",
                    "razon": "[Explicación breve de por qué no hay otras opciones]"
                }}
            ],
            "justificacion_general": "[Escribe aquí el párrafo completo, fluido y sin viñetas que combine los aspectos positivos, beneficios y la justificación pedagógica de la ruta alternativa]"
        }}
        """

        response_text = self._call_llm(prompt, expect_json=True)
        if not response_text:
            return {
                "restricciones_relajadas": [],
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
                "justificacion_general": f"Error al procesar el análisis. Detalles: {str(e)}"
            }