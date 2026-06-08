from collections import deque
from metrics import SearchMetrics
import json
import heapq

class Planner:
    def __init__(self, start_skills, goal_skills, modalities, difficulties, money, time):
        with open('dataset.json', 'r', encoding='utf-8') as f:   #modelo STRIPS
            data = json.load(f)
        self.all_skills = set(data['available_skills'])      #P: conjunto de todas las habilidades disponibles
        self.start_skills = set(start_skills)                #I: conjunto de habilidades iniciales
        self.goal_skills = set(goal_skills)                  #G: conjunto de habilidades objetivo final 
        self.operators = []                                  #O: conjunto de operadores (cursos)
        for course in data['courses']:
            operator = {
                'id': course['id'],                          #identificacion del curso             
                'modality': course['modality'],              #modalidad del curso
                "difficulty": course['difficulty'],          #dificultad del curso
                'alpha': set(course['prerequisites']),       #alpha: conjunto de condiciones que debebn ser verdaderas (prerequisitos del curso)
                'beta' : set(),                              #beta: conjunto de condiciones que deben ser falsas (en este caso es un conjunto vacio)
                'gamma': set(course['effects']),             #gamma: Condiciones que se hacen verdaderas (efectos del curso) (Add List)
                'delta': {                                   #delta: codicones que se hacen falsas, en etse modelo delta representa el consumo de productos, dinero y tiempo (delete list)
                    'money': course.get('cost', 0),
                    'time': course.get('duration_hours', 0)
                }
            }
            self.operators.append(operator)
        self.extra_prerequisites = { 'modalities': modalities,'difficulties': difficulties}      #prerequisitos extras(ej. "solo cursos online", etc)
        self.resources = {'money': money, 'time': time}                                          #recursos dinamicos (ej. "necesito cumplir el plan en 3 meses", etc)

    def is_applicable(self, current_skills, current_resources, operator):
        if not operator['alpha'].issubset(current_skills):                                     #verifica si los prerequisitos que necesita el curso estan dentro de las habilidades actuales
            return False 
        if current_skills.intersection(operator['beta']):                           
            return False 
        
        if operator['gamma'].issubset(current_skills):                                        #verifica si los efectos del curso ya estan entre las habilidades del usurio
            return False

        if operator['modality'] not in self.extra_prerequisites.get('modalities', []):        #verifica si la modalidad del curso estan entre las que desea el usurio
            return False
        if operator['difficulty'] not in self.extra_prerequisites.get('difficulties', []):    #verifica si la dificultad del curso esta entre las que desea el usurio
            return False
        
        if operator['delta']['money'] > current_resources.get('money', 0):                    #verifica si el costo del curso excede los recursos disponibles
            return False
        if operator['delta']['time'] > current_resources.get('time', 0):                      #verifica si la duración del curso excede el tiempo disponible
            return False
        
        return True

    def get_succesor(self, current_skills, current_resources, operator):
        next_skills = current_skills.union(operator['gamma'])                           #agrega las nuevas habilidades a las habilidades actuales
        next_resources = {
            'money': current_resources['money'] - operator['delta']['money'],           #disminuye el costo del curso del presupuesto actual
            'time': current_resources['time'] - operator['delta']['time']               #disminuye la duración del curso del tiempo disponible
        }
        return next_skills, next_resources


    def run_bfs_planner(self):         #Garantiza la primera ruta que encuantra con el menor numero de cursos
        metrics = SearchMetrics()      #inicializa la clase SearchMetrics para  auditar el rendimiento del sistema
        metrics.start_timer()

        queue = deque([(self.start_skills, self.resources, [])])   #Cola que almacena tuplas de: (habilidades_actuales, recursos_disponibles, camino_recorrido)
        visited = {frozenset(self.start_skills)}                   #Conjunto de habilidades obtenidas para evitar ciclos infinitos
         
        while queue:
            current_skills, current_resources, path = queue.popleft() #Extrae el primer nodo de la cola
            metrics.nodes_expanded += 1                               #Registra la expansion del nodo actual
            
            if self.goal_skills.issubset(current_skills):   #Condidicion de parada, verifica si las habilidades objetivos son un subconjunto de las habilidades actuales
                metrics.stop_timer()
                metrics.path_length = len(path)
                return path, metrics     #retorna la ruta optima y las metricas
            
            for operator in self.operators:
                if operator in path:        #no visitar los cursos que ya estan en la ruta
                    continue

                if self.is_applicable(current_skills, current_resources, operator):                             #Verifica que se cumplen los prerequisitos del curso (Alpha) y restricciones fisicas de los recursos
                    next_skills, next_resources = self.get_succesor(current_skills, current_resources, operator)  # Aplica la lista de adición (Gamma) y computa el consumo de recursos (Delta)
                    state_signature = frozenset(next_skills)  
                    
                    if state_signature not in visited:       # Si el estado resultante no ha sido explorado, se añade a la lista
                        visited.add(state_signature)
                        queue.append((next_skills, next_resources, path + [operator]))
        
        metrics.stop_timer()
        return [], metrics  #si no hay camino retorna la lista vacia 

    def run_ucs_planner(self, w_money=0.5, w_time=0.5):  #Garantiza la ruta de menor costo real ponderado basándose en el precio monetario y tiempo
        metrics = SearchMetrics()               #inicializa la clase SearchMetrics para  auditar el rendimiento del sistema
        metrics.start_timer()
        
        queue = []                    #Cola de prioridad (Min-Heap) para extraer siempre el camino con menor costo acumulado
        counter = 0                   # Rompeempates para evitar comparar diccionarios/sets directamente en el Heap

        max_money = self.resources.get('money', 1) if self.resources.get('money', 0) > 0 else 1    #evita la division por 0
        max_time = self.resources.get('time', 1) if self.resources.get('time', 0) > 0 else 1

        start_signature = frozenset(self.start_skills)
        best_cost = {start_signature: 0.0}    #diccionario para manejar segun el conjunto de habilidades cual ha sido el camino menos costoso

        heapq.heappush(queue, (0.0, counter, (self.start_skills, self.resources, [], 0.0)))    #inserta el nodo raizInserta el nodo raíz: (costo acumulado, numero de nodos hasta ahora, (habilidades, recursos, camino, g_puro))
        counter += 1   

        while queue:
            current_cost, _, (current_skills, current_resources, path, g_value) = heapq.heappop(queue) # Extrae el camino con el costo ponderado g(n) más bajo
            state_signature = frozenset(current_skills)

            metrics.nodes_expanded += 1

            if best_cost.get(state_signature, float('inf')) < current_cost:   #si exite un camino mas barato para el mismo conjunto de habilidades no toma este y continua
                continue

            if self.goal_skills.issubset(current_skills):  #Condidicion de parada, verifica si las habilidades objetivos son un subconjunto de las habilidades actuales
                metrics.stop_timer()
                metrics.path_length = len(path)
                return path, metrics
 
            for operator in self.operators:       #no visitar los cursos que ya estan en la ruta
                if operator in path:
                    continue

                if not self.is_applicable(current_skills, current_resources, operator):             #si el curso no se puede aplicar continuar
                    continue

                next_skills, next_resources = self.get_succesor(current_skills, current_resources, operator)   #se anaden las nuevas habilidades obtenidas
                next_signature = frozenset(next_skills)

                pct_money = operator['delta']['money'] / max_money           #Calcula que fraccion del presupuesto y del tiempo total consume el dinero y tiempo de este curso
                pct_time = operator['delta']['time'] / max_time
                step_cost = (w_money * pct_money) + (w_time * pct_time)       #Combina dinero y tiempo
                next_cost = g_value + step_cost                          #suma el costo del curso actual con el costo total de los cursos previos

                if next_signature not in best_cost or next_cost < best_cost[next_signature]:   # Si encontramos un camino más barato hacia este conjunto de habilidades, actualizamos e insertamos
                    best_cost[next_signature] = next_cost
                    heapq.heappush(queue, (next_cost, counter, (next_skills, next_resources, path + [operator], next_cost)))
                    counter += 1

        metrics.stop_timer()
        return [], metrics             #si no hay camino retorna vacio
    
    def heuristic(self, current_skills):        #funcion de heuristica
        missing_skills = self.goal_skills - current_skills # Calcula la diferencia de conjuntos para conocer qué habilidades faltan por adquirir
        if not missing_skills:
            return 0
        
        useful_operators = []       # Filtra los operadores que aporten directamente al menos una habilidad de las faltantes
        for op in self.operators:
            if op['gamma'].intersection(missing_skills):
                useful_operators.append(op)
                
        if not useful_operators:    # Si quedan metas por cumplir pero ningún curso aporta a ellas, es un callejón sin salida (Costo infinito)
            return float('inf')
        
        max_useful_skills = 0         # Encuentra el curso que aporta más habilidades deseadas a la vez
        for op in useful_operators:
            habilidades_utiles = len(op['gamma'].intersection(missing_skills))
            if habilidades_utiles > max_useful_skills:
                max_useful_skills = habilidades_utiles
                
        return (len(missing_skills) ** 2) / max(1, max_useful_skills)    # Retorna una penalización no lineal proporcional a las habilidades faltantes 
    
    def run_astar_planner(self, w_courses=0.40, w_money=0.30, w_time=0.30):    #ejecuta la busqueda con heuristicas
        metrics = SearchMetrics()              #inicializa la clase SearchMetrics para  auditar el rendimiento del sistema
        metrics.start_timer()

        queue = []                         #Cola de prioridad (Min-Heap) para extraer siempre el camino con menor costo acumulado
        counter = 0                   # Rompeempates para evitar comparar diccionarios/sets directamente en el Heap
        

        max_money = self.resources.get('money', 1) if self.resources.get('money', 0) > 0 else 1        #para evitar la division por 0
        max_time = self.resources.get('time', 1) if self.resources.get('time', 0) > 0 else 1

        h_value = self.heuristic(self.start_skills)     # Calcula la estimación inicial h(n) desde el estado de origen

        start_signature = frozenset(self.start_skills)
        best_g = {start_signature: 0.0}          #diccionario para manejar segun el conjunto de habilidades cual ha sido el camino menos costoso
        h_value = h_value * w_courses          # Ponderación inicial del peso del camino

        heapq.heappush(queue, (h_value, counter, (self.start_skills, self.resources, [], 0.0)))      #inserta el nodo raizInserta el nodo raíz: (costo acumulado, numero de nodos hasta ahora, (habilidades, recursos, camino, g_puro))
        counter += 1

        while queue:
            f_value, _, (current_skills, current_resources, path, g_value) = heapq.heappop(queue)    #extrae el primer nodo
            state_signature = frozenset(current_skills)
            metrics.nodes_expanded += 1

            if best_g.get(state_signature, float('inf')) < g_value:      #si existe un camino mas optimo para el mismo conjunto de habilidades no continua
                continue

            if self.goal_skills.issubset(current_skills):    #condicion de parada, si las habilidades objetivos son subconjunto de las habilidades actuales retorna el camino actual
                metrics.stop_timer()
                metrics.path_length = len(path)
                return path, metrics

            for operator in self.operators:            #evita ciclos infinitos
                if operator in path:
                    continue

                if not self.is_applicable(current_skills, current_resources, operator):     #si no es aplicable no continua
                    continue

                next_skills, next_resources = self.get_succesor(current_skills, current_resources, operator)       #anade las nuevas habilidades a la lista
                next_signature = frozenset(next_skills)
                
                # Evaluación multidimensional del costo del paso (Cursos + Presupuesto + Duración)
                pct_money = operator['delta']['money'] / max_money   
                pct_time = operator['delta']['time'] / max_time
                step_cost = (w_courses * 1) + (w_money * pct_money) + (w_time * pct_time)
                g_next = g_value + step_cost     #g(n) del nodo hijo

                if next_signature not in best_g or g_next < best_g[next_signature]:   # Si es un camino más corto en términos reales de 'g', calculamos su f(n)
                    best_g[next_signature] = g_next
                    
                    h_next = self.heuristic(next_skills)     #se calcula la heuristica
                    if h_next == float('inf'):
                        continue
                        
                    f_next = g_next + (h_next * w_courses)  # Función de evaluación definitiva de A*: f(n) = g(n) + h(n)

                    heapq.heappush(queue, (f_next, counter, (next_skills, next_resources, path + [operator], g_next)))
                    counter += 1

        metrics.stop_timer()
        return [], metrics    #si no hay camino retorna []
    
    def get_user_constraints_profile(self):    #Analiza e identifica cuáles restricciones del usuario están activas
        has_modality_constraint = len(self.extra_prerequisites.get('modalities', [])) < 3        # Si hay menos de 3 modalidades en la lista, significa que el usuario explícitamente bloqueó alguna
        has_difficulty_constraint = len(self.extra_prerequisites.get('difficulties', [])) < 3   # Si hay menos de 3 dificultades, el usuario filtró niveles académicos de forma estricta
        has_money_constraint = self.resources.get('money', 0) < 9999999999                       # Evalúa si los límites numéricos de dinero y tiempo poseen topes reales acotados
        has_time_constraint = self.resources.get('time', 0) < 9999999999

        return {
            'modality': has_modality_constraint,
            'difficulty': has_difficulty_constraint,
            'money': has_money_constraint,
            'time': has_time_constraint
        }

    def get_relaxation_score(self, original_modalities, original_difficulties, original_money, original_time):   #Métrica matemática cuantitativa para evaluar el 'castigo' o impacto de una relajación.
        score = 0.0
    
        if self.extra_prerequisites.get('modalities', []) != original_modalities:      # Castigo plano de 1.0 si se alteraron los catálogos discretos de modalidad o dificultad
            score += 1.0
        if self.extra_prerequisites.get('difficulties', []) != original_difficulties:
            score += 1.0

      
        if self.resources.get('money', 0) != original_money:                     # Cálculo del desvío porcentual continuo para el dinero incrementado
            if original_money > 0:
                score += abs(self.resources['money'] - original_money) / original_money
            else:
                score += 1.0

        if self.resources.get('time', 0) != original_time:                  # Cálculo del desvío porcentual continuo para el dinero incrementado
            if original_time > 0:
                score += abs(self.resources['time'] - original_time) / original_time
            else:
                score += 1.0

        return score

    def run_adaptive_planner(self):      #Si la búsqueda estricta falla debido a restricciones incompatibles, escoge la ruta con menor costo de sacrificio
        strict_plan = self.run_astar_planner()      # Ejecutar la planificación bajo el criterio del 100% de restricciones del usuario
        if strict_plan:
            return 'strict_success', strict_plan     # Si la lista de la ruta no está vacía, éxito absoluto
        

        original_modalities = list(self.extra_prerequisites.get('modalities', []))          #Guardar las condiciones iniciales para poder restaurarlas o calcular desvíos
        original_difficulties = list(self.extra_prerequisites.get('difficulties', []))
        original_money = self.resources.get('money', 0)
        original_time = self.resources.get('time', 0)

        all_modalities = ['online','presencial','mixto']
        all_difficulties = ['baja','media','alta']

        profile = self.get_user_constraints_profile()      # Extrae el mapa de restricciones activas del usuario para saber qué mutar
        candidates = []

        if profile['money']:      #Si puso limite de dinero, incrementar un 30% el presupuesto financiero de forma aislada
            candidates.append({
                'modalities': original_modalities, 'difficulties': original_difficulties,
                'money': int(original_money * 1.30), 'time': original_time
            })
        if profile['time']:          #Si puso limite de tiempo, incrementar un 30% la holgura de tiempo disponible de forma aislada
            candidates.append({
                'modalities': original_modalities, 'difficulties': original_difficulties,
                'money': original_money, 'time': int(original_time * 1.30)
            })
        if profile['modality']:      #si restringio las modalidades, habilitar todas las modalidades físicas y virtuales disponibles
            candidates.append({
                'modalities': all_modalities, 'difficulties': original_difficulties,
                'money': original_money, 'time': original_time
            })
        if profile['difficulty']:      #si restringio la dificultad, permitir la inclusión de cualquier nivel de complejidad en los cursos
            candidates.append({
                'modalities': original_modalities, 'difficulties': all_difficulties,
                'money': original_money, 'time': original_time
            })

        candidates.append({               #Relajar de golpe todos los parámetros en un 30% (Margen de seguridad amplio)    
            'modalities': all_modalities if profile['modality'] else original_modalities,
            'difficulties': all_difficulties if profile['difficulty'] else original_difficulties,
            'money': int(original_money * 1.30) if profile['money'] else original_money,
            'time': int(original_time * 1.30) if profile['time'] else original_time
        })

        best_plan = None
        best_score = float('inf')
        forced_mode_activated = False
        best_candidate = None

        for candidate in candidates:         # Evaluación empírica de cada sub-grafo alternativo generado
            self.extra_prerequisites['modalities'] = candidate['modalities']          # Mutación temporal de las propiedades del planificador con los parámetros del candidato
            self.extra_prerequisites['difficulties'] = candidate['difficulties']
            self.resources['money'] = candidate['money']
            self.resources['time'] = candidate['time']

            relaxed_plan = self.run_astar_planner()       # Re-ejecuta el algoritmo en el grafo mutado
            if relaxed_plan:    # Si este escenario abrió un camino viable hacia los objetivo. Calcula el costo matemático de haber roto las restricciones originales
                score = self.get_relaxation_score(
                    original_modalities,
                    original_difficulties,
                    original_money,
                    original_time
                )

                if score < best_score:        # Conservar la ruta con menor penalización para el usuario
                    best_score = score
                    best_plan = relaxed_plan
                    best_candidate = candidate

        if best_plan is None:    #Si las relajaciones leves fallaron por completo
            self.extra_prerequisites['modalities'] = all_modalities      # Se rompen todas las barreras físicas y filtros del grafo para garantizar una ruta didáctica
            self.extra_prerequisites['difficulties'] = all_difficulties
            self.resources['money'] = float('inf')
            self.resources['time'] = float('inf')

            forced_plan = self.run_astar_planner()
            if forced_plan:
                best_plan = forced_plan
                forced_mode_activated = True       # Bandera de advertencia crítica para el LLM

        self.extra_prerequisites['modalities'] = original_modalities
        self.extra_prerequisites['difficulties'] = original_difficulties
        self.resources['money'] = original_money
        self.resources['time'] = original_time

        if best_plan:         
            if forced_mode_activated:
                return 'forced_success', best_plan       # Ruta hallada rompiendo el 100% de límites
            return 'relaxed_success', best_plan         # Ruta hallada minimizando el sacrificio

        return 'failed', []            # Caso crítico: Imposible resolver con el dataset actual