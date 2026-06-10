import json
from pprint import pprint
import time
import os
import sys

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from planner import Planner

test_cases_easy = [
    {
        'name': 'Test1: JS y Desarrollo Web (BFS vs UCS)',
        'difficulties_extracted': ['baja', 'media'],
        'goals_extracted': ['javascript_programming', 'desarrollo_web','python_programming'],
        'modalities_extracted': ['online', 'mixto', 'presencial'],
        'money_extracted': 500,
        'start_skills_extracted': [],
        'time_hours_extracted': 240
    },
    {
        'name': 'Test2: Bases de Datos y SQL (Camino corto caro vs largo barato)',
        'difficulties_extracted': ['baja', 'media','alta'],
        'goals_extracted': ['sql', 'bases_de_datos'],
        'modalities_extracted': ['online', 'mixto', 'presencial',],
        'money_extracted': 250,
        'start_skills_extracted': [],
        'time_hours_extracted': 180
    },
    {
        'name': 'Test3: Frontend + Backend + Web (Bootcamp vs Cursos Sueltos)',
        'difficulties_extracted': ['baja', 'media'],
        'goals_extracted': ['desarrollo_web', 'frontend_web', 'backend_web'],
        'modalities_extracted': ['online'],
        'money_extracted': 300,
        'start_skills_extracted': [],
        'time_hours_extracted': 250
    },
    {
        'name': 'Test4: Cloud y DevOps (Optimización de costes con base)',
        'difficulties_extracted': ['media', 'alta'],
        'goals_extracted': ['cloud_computing', 'devops'],
        'modalities_extracted': ['online','presencial'],
        'money_extracted': 1000,
        'start_skills_extracted': ['programacion_basica'],
        'time_hours_extracted': 300
    },
    {
        'name': 'Test5: Python Programming desde Cero',
        'difficulties_extracted': ['media'],
        'goals_extracted': ['programacion_orientada_objetos'],
        'modalities_extracted': ['online', 'presencial'],
        'money_extracted': 200,
        'start_skills_extracted': [],
        'time_hours_extracted': 100
    },
    {
        'name': 'Test6: DevOps Pro Avanzado',
        'difficulties_extracted': ['baja', 'media', 'alta'],
        'goals_extracted': ['devops'],
        'modalities_extracted': ['online', 'mixto','presencial'],
        'money_extracted': 250,
        'start_skills_extracted': ['version_control'],
        'time_hours_extracted': 200
    },
    {
        'name': 'Test7: Software Testing con Presupuesto',
        'difficulties_extracted': ['baja', 'media'],
        'goals_extracted': ['software_testing'],
        'modalities_extracted': ['online', 'mixto'],
        'money_extracted': 250,
        'start_skills_extracted': [],  
        'time_hours_extracted': 100
    },
    {
        'name': 'Test8: Mobile + UI/UX + Testing (Megabootcamp vs Cursos Cortos)',
        'difficulties_extracted': ['baja', 'media'],
        'goals_extracted': ['mobile_development', 'ui_ux'],
        'modalities_extracted': ['online','presencial'],
        'money_extracted': 250,
        'start_skills_extracted': [],
        'time_hours_extracted': 220
    },
    {
        'name': 'Test9: Machine learning and deep learning',
        'difficulties_extracted': ['baja', 'media', 'alta'],
        'goals_extracted': ['deep_learning'],
        'modalities_extracted': ['online', 'mixto', 'presencial'],
        'money_extracted': 5000,
        'start_skills_extracted': ['python_programming'],
        'time_hours_extracted': 1200
    },
    {
        'name': 'Test10: IA Completa vs Ruta Tradicional',
        'difficulties_extracted': ['baja', 'media', 'alta'],
        'goals_extracted': ['inteligencia_artificial'],
        'modalities_extracted': ['online', 'mixto', 'presencial'],
        'money_extracted': 1000000,
        'start_skills_extracted': [],
        'time_hours_extracted': 1000000
    }
]

test_cases_hard = [
    {
        'name': 'test11: Necesita relajar modalidad',
        'difficulties_extracted': ['baja','media','alta'],
        'goals_extracted': ['version_control'],
        'modalities_extracted': ['mixto'],
        'money_extracted': 5000,
        'start_skills_extracted': [],
        'time_hours_extracted': 500
    },
    {
        'name': 'test12: Necesita relajar dificultad',
        'difficulties_extracted': [ 'alta'],
        'goals_extracted': ['javascript_programming'],
        'modalities_extracted': ['online', 'mixto', 'presencial'],
        'money_extracted': 2000,
        'start_skills_extracted': [],
        'time_hours_extracted': 280 
    },
    {
        'name': 'test13: Necesita relajar dinero',
        'difficulties_extracted': ['baja','media','alta'],
        'goals_extracted': ['redes_computadoras'],
        'modalities_extracted': ['online', 'mixto', 'presencial'],
        'money_extracted': 30, 
        'start_skills_extracted': [],
        'time_hours_extracted': 400
    },
    {
        'name': 'test14: Necesita relajar Tiempo',
        'difficulties_extracted': ['baja','media','alta'],
        'goals_extracted': ['criptografia'],
        'modalities_extracted': ['online', 'mixto', 'presencial'],
        'money_extracted': 10000000,
        'start_skills_extracted': ['logica_matematica', 'ciberseguridad_fundamentos'],
        'time_hours_extracted': 10
    }
]

test_cases = test_cases_easy + test_cases_hard

def test_planner_variant(variant_name, start_skills, goal_skills, modalities, difficulties, money, time_hours):
    print(f"Testing: {variant_name}")
    print(f"{'='*80}")
    print(f"Start skills: {start_skills}")
    print(f"Goal skills: {goal_skills}")
    print(f"Modalities: {modalities}")
    print(f"Difficulties: {difficulties}")
    print(f"Money: {money}")
    print(f"Time (hours): {time_hours}")
    
    try:
        planner = Planner(start_skills, goal_skills, modalities, difficulties, money, time_hours)
        
       
        if variant_name == "BFS":
            result, metrics = planner.run_bfs_planner()
        elif variant_name == "UCS":
            result, metrics = planner.run_ucs_planner()
        elif variant_name == "A*":
            result, metrics = planner.run_astar_planner()
        elif variant_name == "Adaptive":
            mode, result = planner.run_adaptive_planner()
            print(f"Mode: {mode}")
            
            metrics = type('obj', (object,), {
                'to_dict': lambda _: {
                    "nodes_expanded": "N/A (Adaptive)", 
                    "execution_time_ms": "Ver log", 
                    "path_length": len(result)
                }
            })()
        else:
            result, metrics = [], None
        
        m_dict = metrics.to_dict() if metrics else {"nodes_expanded": 0, "execution_time_ms": 0.0, "path_length": 0}
        
        print(f"\nResult: {len(result)} courses found")
        print(f"Execution time: {m_dict['execution_time_ms']} ms")
        print(f"Nodes expanded: {m_dict['nodes_expanded']}")
        
        if result:
            print("\nCourses in plan:")
            for i, course in enumerate(result, 1):
                print(f"  {i}. {course['id']} (Cost: ${course['delta']['money']}, Duration: {course['delta']['time']}h)")
            
            total_money = sum(c['delta']['money'] for c in result)
            total_time = sum(c['delta']['time'] for c in result)
            print(f"\nTotal cost: ${total_money}")
            print(f"Total duration: {total_time} hours")
        else:
            print("No plan found!")
     
        return {"plan": result, "metrics": m_dict}
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_all_tests(target_index=None):
    all_results = {}
    
    current_easy = test_cases_easy
    current_hard = test_cases_hard
    
    if target_index is not None:
        idx = target_index - 1
        if 0 <= idx < len(test_cases_easy):
            current_easy = [test_cases_easy[idx]]
            current_hard = []
        elif len(test_cases_easy) <= idx < len(test_cases):
            current_easy = []
            current_hard = [test_cases_hard[idx - len(test_cases_easy)]]
        else:
            print(f"ERROR: El índice {target_index} está fuera de rango. Total de casos: {len(test_cases)}")
            return

    if current_easy:
        print("# GRUPO 1: CASOS FÁCILES - Resolubles con BFS, UCS, A*")
        for test_case in current_easy:
            test_name = test_case['name']
            all_results[test_name] = {}
           
            print(f"\nExecuting: {test_name}")
            
            start_skills = test_case['start_skills_extracted']
            goal_skills = test_case['goals_extracted']
            modalities = test_case['modalities_extracted']
            difficulties = test_case['difficulties_extracted']
            money = test_case['money_extracted']
            time_hours = test_case['time_hours_extracted']
            
            variants = ["BFS", "UCS", "A*"]
            
            for variant in variants:
                res_data = test_planner_variant(
                    variant,
                    start_skills,
                    goal_skills,
                    modalities,
                    difficulties,
                    money,
                    time_hours
                )
                all_results[test_name][variant] = res_data
                time.sleep(0.1)
    
    if current_hard:
        print("\nGRUPO 2: CASOS DIFÍCILES - Requieren Adaptive Planner")
        for test_case in current_hard:
            test_name = test_case['name']
            all_results[test_name] = {}
            
            print(f"\nExecuting: {test_name}")
        
            start_skills = test_case['start_skills_extracted']
            goal_skills = test_case['goals_extracted']
            modalities = test_case['modalities_extracted']
            difficulties = test_case['difficulties_extracted']
            money = test_case['money_extracted']
            time_hours = test_case['time_hours_extracted']
            
            variants = ["Adaptive"]
            
            for variant in variants:
                res_data = test_planner_variant(
                    variant,
                    start_skills,
                    goal_skills,
                    modalities,
                    difficulties,
                    money,
                    time_hours
                )
                all_results[test_name][variant] = res_data
                time.sleep(0.1)
    
    
    print("\n" + "="*105)
    print("                 RESUMEN FINAL DE RENDIMIENTO EXPERIMENTAL Y COMPARATIVO DE IA")
    print("="*105)
    print(f"{'Caso de Prueba / Variante Algorítmica':<45} | {'Status':<13} | {'Tiempo':<13} | {'Nodos Exp.':<14} | {'Long. Ruta':<10}")
    print("-"*105)
   
    if current_easy:
        print(f"🔹 GRUPO 1: EVALUACIÓN DE OPTIMALIDAD Y ESPACIO DE ESTADOS")
        print("-"*105)
        for test_case in current_easy:
            test_name = test_case['name']
    
            short_name = test_name if len(test_name) <= 43 else test_name[:40] + "..."
            print(f"📌 {short_name:<42}")
            
            results = all_results.get(test_name, {})
            for variant in ["BFS", "UCS", "A*"]:
                data = results.get(variant)
                if data and data['plan'] is not None:
                    plan = data['plan']
                    m = data['metrics']
                    
                    status = "OK" if len(plan) > 0 else "Sin Solución"
                    time_str = f"{m['execution_time_ms']} ms" if isinstance(m['execution_time_ms'], (int, float)) else str(m['execution_time_ms'])
                    nodes_str = f"{m['nodes_expanded']} nodos" if isinstance(m['nodes_expanded'], int) else str(m['nodes_expanded'])
                    len_str = f"{m['path_length']} cursos"
                    
                    print(f"   ↳ {variant:<40} | {status:<13} | {time_str:<13} | {nodes_str:<14} | {len_str:<10}")
                else:
                    print(f"   ↳ {variant:<40} | {'Error/No Ejec':<13} | {'--':<13} | {'--':<14} | {'--':<10}")
            print("-"*105)
    
    if current_hard:
        print(f"🔹 GRUPO 2: CASOS COMPLEJOS CON RESTRICCIONES (LOGICA ADAPTATIVA)")
        print("-"*105)
        for test_case in current_hard:
            test_name = test_case['name']
            short_name = test_name if len(test_name) <= 43 else test_name[:40] + "..."
            print(f"📌 {short_name:<42}")
            
            results = all_results.get(test_name, {})
            variant = "Adaptive"
            data = results.get(variant)
            if data and data['plan'] is not None:
                plan = data['plan']
                m = data['metrics']
                
                status = "Relajado OK" if len(plan) > 0 else "Sin Solución"
                time_str = "Satisfecho"
                nodes_str = "Multi-Grafo"
                len_str = f"{m['path_length']} cursos"
                
                print(f"   ↳ {variant:<40} | {status:<13} | {time_str:<13} | {nodes_str:<14} | {len_str:<10}")
            print("-"*105)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        target = int(sys.argv[1])
        run_all_tests(target_index=target)
    else:
        run_all_tests()