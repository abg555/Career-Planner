from collections import deque
import json
import heapq

class Planner:
    def __init__(self, start_skills, goal_skills, extra_prerequisites):
        with open('dataset.json', 'r', encoding='utf-8') as f:   #modelo STRIPS
            data = json.load(f)
        self.all_skills = set(data['available_skills'])      #P: conjunto de todas las habilidades disponibles
        self.start_skills = set(start_skills)                #I: conjunto de habilidades iniciales
        self.goal_skills = set(goal_skills)                  #G: conjunto de habilidades objetivo final 
        self.operators = []                                  #O: conjunto de operadores (cursos)
        for course in data['courses']:
            operator = {
                'id': course['id'],                          #identificacion del curso             
                'title': course['title'],                    #titulo del curso
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
        self.extra_prerequisites = extra_prerequisites       #prerequisitos extras(ej. "presupuesto limitado de 50 dolares", "solo cursos online", etc)

    def is_applicable(self, current_skill, current_resources, operator):
        if not operator['alpha'].issubset(current_skill):
            return False 
        if current_skill.intersection(operator['beta']):
            return False 

        if operator['modality'] not in self.extra_prerequisites.get('modalities', []):
            return False
        if operator['difficulty'] not in self.extra_prerequisites.get('difficulties', []):
            return False
        
        if operator['delta']['money'] > current_resources.get('money', 0):
            return False
        if operator['delta']['time'] > current_resources.get('time', 0):
            return False
        
        return True

    def get_succesor(self, current_skills, current_resources, operator):
        next_skills = current_skills.union(operator['gamma'])
        next_resources = {
            'money': current_resources['money'] - operator['delta']['money'],
            'time': current_resources['time'] - operator['delta']['time']
        }
        return next_skills, next_resources

    def run_bfs_planner(self):
        queue = deque([(self.start_skills, self.extra_prerequisites, [])])
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
    
    