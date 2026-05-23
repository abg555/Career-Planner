import json
from pprint import pprint
from planner import Planner
import time

test_cases_easy = [
    {
        'name': 'Easy 1: Frontend Developer - Multiples rutas (corta cara vs larga barata)',
        'difficulties_extracted': ['baja', 'media', 'alta'],
        'goals_extracted': ['frontend_web', 'javascript_programming', 'desarrollo_web'],
        'modalities_extracted': ['online'],
        'money_extracted': 500,
        'start_skills_extracted': [],
        'time_hours_extracted': 240
    },
    {
        'name': 'Easy 2: Database Expert - SQL practico vs Bases de Datos I',
        'difficulties_extracted': ['baja', 'media'],
        'goals_extracted': ['sql', 'bases_de_datos'],
        'modalities_extracted': ['online'],
        'money_extracted': 200,
        'start_skills_extracted': [],
        'time_hours_extracted': 120
    },
    {
        'name': 'Easy 3: Web Developer - Fullstack Bootcamp vs Cursos individuales',
        'difficulties_extracted': ['baja', 'media', 'alta'],
        'goals_extracted': ['desarrollo_web', 'frontend_web', 'backend_web'],
        'modalities_extracted': ['online', 'mixto'],
        'money_extracted': 300,
        'start_skills_extracted': [],
        'time_hours_extracted': 250
    },
    {
        'name': 'Easy 4: Cloud Basics - Cloud basics gratuito vs Cloud y DevOps',
        'difficulties_extracted': ['baja', 'media'],
        'goals_extracted': ['cloud_computing', 'devops'],
        'modalities_extracted': ['online'],
        'money_extracted': 150,
        'start_skills_extracted': ['programacion_basica'],
        'time_hours_extracted': 150
    },
    {
        'name': 'Easy 5: Data Basics - Python y Estadistica',
        'difficulties_extracted': ['baja', 'media'],
        'goals_extracted': ['python_programming'],
        'modalities_extracted': ['online', 'mixto'],
        'money_extracted': 200,
        'start_skills_extracted': [],
        'time_hours_extracted': 100
    },
    {
        'name': 'Easy 6: DevOps Path - DevOps y Cloud (multiple rutas)',
        'difficulties_extracted': ['media', 'alta'],
        'goals_extracted': ['devops', 'cloud_computing'],
        'modalities_extracted': ['online', 'mixto'],
        'money_extracted': 250,
        'start_skills_extracted': ['programacion_basica'],
        'time_hours_extracted': 200
    },
    {
        'name': 'Easy 7: Backend Developer - Backend y desarrollo',
        'difficulties_extracted': ['baja', 'media'],
        'goals_extracted': ['backend_web', 'programacion_orientada_objetos'],
        'modalities_extracted': ['online', 'mixto'],
        'money_extracted': 200,
        'start_skills_extracted': ['programacion_basica'],
        'time_hours_extracted': 150
    },
    {
        'name': 'Easy 8: Testing and Quality - Testing skills',
        'difficulties_extracted': ['baja', 'media'],
        'goals_extracted': ['software_testing'],
        'modalities_extracted': ['online', 'mixto'],
        'money_extracted': 150,
        'start_skills_extracted': ['programacion_basica'],
        'time_hours_extracted': 100
    },
    {
        'name': 'Easy 9: Mobile Product - ruta corta, barata e intermedia',
        'difficulties_extracted': ['baja'],
        'goals_extracted': ['mobile_development', 'ui_ux', 'software_testing'],
        'modalities_extracted': ['online'],
        'money_extracted': 250,
        'start_skills_extracted': [],
        'time_hours_extracted': 220
    },
    {
        'name': 'Easy 10: Web + Cloud - tres salidas diferentes',
        'difficulties_extracted': ['baja', 'media', 'alta'],
        'goals_extracted': ['frontend_web', 'cloud_computing'],
        'modalities_extracted': ['online', 'mixto', 'presencial'],
        'money_extracted': 500,
        'start_skills_extracted': [],
        'time_hours_extracted': 300
    },
    {
        'name': 'Easy 11: Frontend + ML - directa, barata y mixta',
        'difficulties_extracted': ['baja', 'media', 'alta'],
        'goals_extracted': ['frontend_web', 'machine_learning'],
        'modalities_extracted': ['online', 'mixto', 'presencial'],
        'money_extracted': 500,
        'start_skills_extracted': [],
        'time_hours_extracted': 320
    }
]

test_cases_hard = [
    {
        'name': 'Hard 1: Data Scientist - NECESITA RELAJAR MODALIDAD (solo presencial)',
        'difficulties_extracted': ['alta'],
        'goals_extracted': ['machine_learning', 'deep_learning', 'data_science'],
        'modalities_extracted': ['presencial'],  # RESTRICCIÓN: Solo presencial (hay cursos solo online)
        'money_extracted': 5000,
        'start_skills_extracted': ['python_programming', 'estadistica'],
        'time_hours_extracted': 500
    },
    {
        'name': 'Hard 2: AI Course - NECESITA RELAJAR TIEMPO (tiempo muy restringido)',
        'difficulties_extracted': ['media', 'alta'],
        'goals_extracted': ['inteligencia_artificial', 'machine_learning'],
        'modalities_extracted': ['online', 'mixto', 'presencial'],
        'money_extracted': 2000,
        'start_skills_extracted': ['estructuras_datos', 'logica_matematica'],
        'time_hours_extracted': 280  # RESTRICCION: Solo 280 horas (restrictivo pero alcanzable)
    },
    {
        'name': 'Hard 3: Security Expert - NECESITA RELAJAR DINERO (presupuesto muy bajo)',
        'difficulties_extracted': ['alta'],
        'goals_extracted': ['ciberseguridad_fundamentos', 'seguridad_informatica', 'criptografia'],
        'modalities_extracted': ['online', 'mixto', 'presencial'],
        'money_extracted': 50,  # RESTRICCION: Solo $50 (muy poco, necesita relajar dinero)
        'start_skills_extracted': ['redes_computadoras'],
        'time_hours_extracted': 400
    },
    {
        'name': 'Hard 4: Fullstack Developer - NECESITA RELAJAR DINERO Y TIEMPO',
        'difficulties_extracted': ['baja'],  # RESTRICCIÓN: Solo baja dificultad
        'goals_extracted': ['desarrollo_web', 'frontend_web', 'backend_web', 'bases_de_datos'],
        'modalities_extracted': ['online', 'mixto', 'presencial'],
        'money_extracted': 24,
        'start_skills_extracted': [],
        'time_hours_extracted': 90
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
        
        start_time = time.time()
        
        if variant_name == "BFS":
            result = planner.run_bfs_planner()
        elif variant_name == "UCS":
            result = planner.run_ucs_planner()
        elif variant_name == "A*":
            result = planner.run_astar_planner()
        elif variant_name == "Adaptive":
            mode, result = planner.run_adaptive_planner()
            print(f"Mode: {mode}")
        else:
            result = []
        
        elapsed_time = time.time() - start_time
        
        print(f"\nResult: {len(result)} courses found")
        print(f"Execution time: {elapsed_time:.4f} seconds")
        
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
        
        return result
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_all_tests():
    all_results = {}
    
    print("# GRUPO 1: CASOS FÁCILES - Resolubles con BFS, UCS, A*")
    
    for test_case in test_cases_easy:
        test_name = test_case['name']
        all_results[test_name] = {}
       
        print(f"{test_name}")
        
        start_skills = test_case['start_skills_extracted']
        goal_skills = test_case['goals_extracted']
        modalities = test_case['modalities_extracted']
        difficulties = test_case['difficulties_extracted']
        money = test_case['money_extracted']
        time_hours = test_case['time_hours_extracted']
        
        variants = ["BFS", "UCS", "A*"]
        
        for variant in variants:
            result = test_planner_variant(
                variant,
                start_skills,
                goal_skills,
                modalities,
                difficulties,
                money,
                time_hours
            )
            all_results[test_name][variant] = result
            time.sleep(0.2)
    
    print("GRUPO 2: CASOS DIFÍCILES - Requieren Adaptive Planner")

    
    for test_case in test_cases_hard:
        test_name = test_case['name']
        all_results[test_name] = {}
        
       
        print(f"{test_name}")
       
    
        start_skills = test_case['start_skills_extracted']
        goal_skills = test_case['goals_extracted']
        modalities = test_case['modalities_extracted']
        difficulties = test_case['difficulties_extracted']
        money = test_case['money_extracted']
        time_hours = test_case['time_hours_extracted']
        
        variants = ["Adaptive"]
        
        for variant in variants:
            result = test_planner_variant(
                variant,
                start_skills,
                goal_skills,
                modalities,
                difficulties,
                money,
                time_hours
            )
            all_results[test_name][variant] = result
            time.sleep(0.2)
    
  
    print("RESUMEN FINAL")
   
    print("\n\n[*] GRUPO 1: CASOS FACILES (BFS, UCS, A*)")
    print("-" * 80)
    for test_case in test_cases_easy:
        test_name = test_case['name']
        results = all_results[test_name]
        successful = sum(1 for r in results.values() if r and len(r) > 0)
        print(f"  {test_name}")
        for variant, result in results.items():
            status = f"[OK] {len(result)} cursos" if result and len(result) > 0 else "[--] Sin solucion"
            print(f"    {variant:25} {status}")
    
    print("\n\n[*] GRUPO 2: CASOS DIFICILES (Adaptive)")
    print("-" * 80)
    for test_case in test_cases_hard:
        test_name = test_case['name']
        results = all_results[test_name]
        print(f"  {test_name}")
        for variant, result in results.items():
            status = f"[OK] {len(result)} cursos" if result and len(result) > 0 else "[--] Sin solucion"
            print(f"    {variant:25} {status}")



if __name__ == '__main__':
    run_all_tests()
