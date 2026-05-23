from collections import deque
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

    def _summarize_plan(self, plan):
        if not plan:
            return {
                'courses': [],
                'total_money': 0,
                'total_time': 0
            }

        return {
            'courses': [course['id'] for course in plan],
            'total_money': sum(course['delta']['money'] for course in plan),
            'total_time': sum(course['delta']['time'] for course in plan)
        }

    def _print_state(self, title, modalities, difficulties, money, time):
        print(f"\n{title}")
        print(f"  Modalities : {modalities}")
        print(f"  Difficulties: {difficulties}")
        print(f"  Money       : {money}")
        print(f"  Time        : {time}")

    def _print_plan(self, title, plan):
        summary = self._summarize_plan(plan)
        print(f"\n{title}")
        print(f"  Courses : {summary['courses']}")
        print(f"  Money   : ${summary['total_money']}")
        print(f"  Time    : {summary['total_time']}h")

    def run_bfs_planner(self):
        queue = deque([(self.start_skills, self.resources, [])])
        visited = {frozenset(self.start_skills)}
        
        while queue:
            current_skills, current_resources, path = queue.popleft()
            
            if self.goal_skills.issubset(current_skills):
                return path
            
            for operator in self.operators:
                if operator in path:
                    continue

                if self.is_applicable(current_skills, current_resources, operator):
                    next_skills, next_resources = self.get_succesor(current_skills, current_resources, operator)
                    state_signature = frozenset(next_skills)
                    
                    if state_signature not in visited:
                        visited.add(state_signature)
                        queue.append((next_skills, next_resources, path + [operator]))
        return []

    def run_ucs_planner(self, w_money=0.5, w_time=0.5):
        queue = []
        counter = 0

        max_money = self.resources.get('money', 1) if self.resources.get('money', 0) > 0 else 1
        max_time = self.resources.get('time', 1) if self.resources.get('time', 0) > 0 else 1

        start_signature = (frozenset(self.start_skills), self.resources['money'], self.resources['time'])
        best_cost = {start_signature: 0.0}

        heapq.heappush(queue, (0.0, counter, (self.start_skills, self.resources, [], 0.0)))
        counter += 1

        while queue:
            current_cost, _, (current_skills, current_resources, path, g_value) = heapq.heappop(queue)
            state_signature = (frozenset(current_skills), current_resources['money'], current_resources['time'] )

            if best_cost.get(state_signature, float('inf')) < current_cost:
                continue

            if self.goal_skills.issubset(current_skills):
                return path

            for operator in self.operators:
                if operator in path:
                    continue

                if not self.is_applicable(current_skills, current_resources, operator):
                    continue

                next_skills, next_resources = self.get_succesor(current_skills, current_resources, operator)
                next_signature = (frozenset(next_skills),next_resources['money'],next_resources['time'])

                pct_money = operator['delta']['money'] / max_money
                pct_time = operator['delta']['time'] / max_time
                step_cost = (w_money * pct_money) + (w_time * pct_time)
                next_cost = g_value + step_cost

                if next_signature not in best_cost or next_cost < best_cost[next_signature]:
                    best_cost[next_signature] = next_cost
                    heapq.heappush(queue, (next_cost, counter, (next_skills, next_resources, path + [operator], next_cost)))
                    counter += 1

        return []
    
    def heuristic(self, current_skills):
        missing_skills = self.goal_skills - current_skills
        if not missing_skills:
            return 0
        
        useful_operators = []
        for op in self.operators:
            if op['gamma'].intersection(missing_skills):
                useful_operators.append(op)
                
        if not useful_operators:
            return float('inf')
        
        max_useful_skills = 0
        for op in useful_operators:
            habilidades_utiles = len(op['gamma'].intersection(missing_skills))
            if habilidades_utiles > max_useful_skills:
                max_useful_skills = habilidades_utiles
                
        # Penaliza más fuertemente los estados con más habilidades faltantes,
        # para que A* diferencie mejor entre rutas cortas, baratas y equilibradas.
        return (len(missing_skills) ** 2) / max(1, max_useful_skills)
    
    def run_astar_planner(self, w_courses = 0.40, w_money = 0.30, w_time = 0.30):
        queue = []
        counter = 0

        max_money = self.resources.get('money', 1) if self.resources.get('money', 0) > 0 else 1
        max_time = self.resources.get('time', 1) if self.resources.get('time', 0) > 0 else 1

        h_value = self.heuristic(self.start_skills)

        start_signature = (frozenset(self.start_skills), self.resources['money'], self.resources['time'])
        best_g = {start_signature: 0.0}
        h_value = h_value * w_courses

        heapq.heappush(queue, (h_value, counter, (self.start_skills, self.resources, [], 0.0)))
        counter += 1

        while queue:
            f_value, _, (current_skills, current_resources, path, g_value) = heapq.heappop(queue)
            state_signature = (frozenset(current_skills), current_resources['money'], current_resources['time'])

            if best_g.get(state_signature, float('inf')) < g_value:
                continue

            if self.goal_skills.issubset(current_skills):
                return path

            for operator in self.operators:
                if operator in path:
                    continue

                if not self.is_applicable(current_skills, current_resources, operator):
                    continue

                next_skills, next_resources = self.get_succesor(current_skills, current_resources, operator)
                next_signature = (frozenset(next_skills), next_resources['money'],next_resources['time'])
                
                pct_money = operator['delta']['money'] / max_money
                pct_time = operator['delta']['time'] / max_time
                step_cost = (w_courses * 1) + (w_money * pct_money) + (w_time * pct_time)
                g_next = g_value + step_cost

                if next_signature not in best_g or g_next < best_g[next_signature]:
                    best_g[next_signature] = g_next
                    
                    h_next = self.heuristic(next_skills)
                    
                    if h_next == float('inf'):
                        continue
                        
                    f_next = g_next + (h_next * w_courses)

                    heapq.heappush(queue, (f_next, counter, (next_skills, next_resources, path + [operator], g_next)))
                    counter += 1

        return []
    
    def get_user_constraints_profile(self):
        has_modality_constraint = len(self.extra_prerequisites.get('modalities', [])) < 3
        has_difficulty_constraint = len(self.extra_prerequisites.get('difficulties', [])) < 3
        has_money_constraint = self.resources.get('money', 0) < 9999999999  
        has_time_constraint = self.resources.get('time', 0) < 9999999999

        return {
            'modality': has_modality_constraint,
            'difficulty': has_difficulty_constraint,
            'money': has_money_constraint,
            'time': has_time_constraint
        }

    def get_relaxation_score(self, original_modalities, original_difficulties, original_money, original_time):
        score = 0.0

        if self.extra_prerequisites.get('modalities', []) != original_modalities:
            score += 1.0
        if self.extra_prerequisites.get('difficulties', []) != original_difficulties:
            score += 1.0

        if self.resources.get('money', 0) != original_money:
            if original_money > 0:
                score += abs(self.resources['money'] - original_money) / original_money
            else:
                score += 1.0

        if self.resources.get('time', 0) != original_time:
            if original_time > 0:
                score += abs(self.resources['time'] - original_time) / original_time
            else:
                score += 1.0

        return score

    def run_adaptive_planner(self, verbose=True):
        if verbose:
            print("\n" + "=" * 80)
            print("ADAPTIVE PLANNER")
            print("=" * 80)
            self._print_state(
                "Before relaxation (strict constraints)",
                list(self.extra_prerequisites.get('modalities', [])),
                list(self.extra_prerequisites.get('difficulties', [])),
                self.resources.get('money', 0),
                self.resources.get('time', 0)
            )

        strict_plan = self.run_astar_planner()
        if strict_plan:
            if verbose:
                print("\nStrict search succeeded without relaxing constraints.")
                self._print_plan("Strict plan", strict_plan)
            return 'strict_success', strict_plan
        
        if verbose:
            print("\nStrict search failed. Trying relaxed variants...")

        original_modalities = list(self.extra_prerequisites.get('modalities', []))
        original_difficulties = list(self.extra_prerequisites.get('difficulties', []))
        original_money = self.resources.get('money', 0)
        original_time = self.resources.get('time', 0)

        all_modalities = ['online','presencial','mixto']
        all_difficulties = ['baja','media','alta']

        profile = self.get_user_constraints_profile()
        candidates = []

        if profile['money']:
            candidates.append({
                'modalities': original_modalities, 'difficulties': original_difficulties,
                'money': int(original_money * 1.30), 'time': original_time
            })
        if profile['time']:
            candidates.append({
                'modalities': original_modalities, 'difficulties': original_difficulties,
                'money': original_money, 'time': int(original_time * 1.30)
            })
        if profile['modality']:
            candidates.append({
                'modalities': all_modalities, 'difficulties': original_difficulties,
                'money': original_money, 'time': original_time
            })
        if profile['difficulty']:
            candidates.append({
                'modalities': original_modalities, 'difficulties': all_difficulties,
                'money': original_money, 'time': original_time
            })

        candidates.append({
            'modalities': all_modalities if profile['modality'] else original_modalities,
            'difficulties': all_difficulties if profile['difficulty'] else original_difficulties,
            'money': int(original_money * 1.30) if profile['money'] else original_money,
            'time': int(original_time * 1.30) if profile['time'] else original_time
        })

        best_plan = None
        best_score = float('inf')
        forced_mode_activated = False
        best_candidate = None

        for candidate in candidates:
            self.extra_prerequisites['modalities'] = candidate['modalities']
            self.extra_prerequisites['difficulties'] = candidate['difficulties']
            self.resources['money'] = candidate['money']
            self.resources['time'] = candidate['time']

            relaxed_plan = self.run_astar_planner()
            if relaxed_plan:
                score = self.get_relaxation_score(
                    original_modalities,
                    original_difficulties,
                    original_money,
                    original_time
                )

                if verbose:
                    print("\nRelaxed candidate found:")
                    self._print_state(
                        "Candidate constraints",
                        candidate['modalities'],
                        candidate['difficulties'],
                        candidate['money'],
                        candidate['time']
                    )
                    print(f"  Relaxation score: {score:.3f}")
                    self._print_plan("  Candidate plan", relaxed_plan)

                if score < best_score:
                    best_score = score
                    best_plan = relaxed_plan
                    best_candidate = candidate

        if best_plan is None:
            self.extra_prerequisites['modalities'] = all_modalities
            self.extra_prerequisites['difficulties'] = all_difficulties
            self.resources['money'] = float('inf')
            self.resources['time'] = float('inf')

            forced_plan = self.run_astar_planner()
            if forced_plan:
                best_plan = forced_plan
                forced_mode_activated = True

        self.extra_prerequisites['modalities'] = original_modalities
        self.extra_prerequisites['difficulties'] = original_difficulties
        self.resources['money'] = original_money
        self.resources['time'] = original_time

        if best_plan:
            if verbose:
                print("\nAfter relaxation (selected best plan)")
                if best_candidate is not None:
                    self._print_state(
                        "Relaxed constraints used",
                        best_candidate['modalities'],
                        best_candidate['difficulties'],
                        best_candidate['money'],
                        best_candidate['time']
                    )
                self._print_plan("Selected plan", best_plan)

            if forced_mode_activated:
                return 'forced_success', best_plan
            return 'relaxed_success', best_plan

        if verbose:
            print("\nAdaptive search failed even after relaxation.")

        return 'failed', []