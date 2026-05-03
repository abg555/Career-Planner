from collections import deque
import json
import heapq

class Planner:
    def __init__(self):
        with open('dataset.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def check_prerequisites(self, current_state, course_data):
        prereqs = set(course_data['prerequisites'])
        return prereqs.issubset(current_state)

    def apply_effects(self, current_state, course_data):
        next_state = current_state.copy()
        for effect in course_data['effects']:
            next_state.add(effect)
        return next_state

    def run_bfs_planner(self, start_skills, goal_skills):
        goal_skills_set =  set(goal_skills)
        queue = deque([(set(start_skills), [])])  
        visited = set()

        while queue:
            current_state, path = queue.popleft()
            
            if goal_skills_set.issubset(current_state):
                return path
            
            state_signature = frozenset(current_state)
            if state_signature in visited:
                continue
            visited.add(state_signature)

            for course in self.data['courses']:
                if course['id'] in path:
                    continue
                
                if self.check_prerequisites(current_state, course):
                    new_state = self.apply_effects(current_state, course)
                    queue.append((new_state, path + [course['id']]))

        return []
    
    def run_cost_planner(self, start_skills, goal_skills):
        goal_skills_set = set(goal_skills)
        pq = []
        start_state = set(start_skills)
        heapq.heappush(pq, (0, start_state, []))
        best_cost = {frozenset(start_state): 0}

        while pq:
            cost, current_state, path = heapq.heappop(pq)

            if goal_skills_set.issubset(current_state):
                return path

            state_sig = frozenset(current_state)
            if cost > best_cost.get(state_sig, float('inf')):
                continue

            for course in self.data['courses']:
                if course['id'] in path:
                    continue

                if self.check_prerequisites(current_state, course):
                    new_state = self.apply_effects(current_state, course)
                    new_cost = cost + course.get('cost', 0)
                    new_sig = frozenset(new_state)

                    if new_cost < best_cost.get(new_sig, float('inf')):
                        best_cost[new_sig] = new_cost
                        heapq.heappush(pq, (new_cost, new_state, path + [course['id']]))

        return []
                    