import os
import json
import time
import sys
from dotenv import load_dotenv
from llm_interface import LLMInterface
from planner import Planner


load_dotenv()

def run_pipeline_test():
    print("================================================================================")
    print("              INICIANDO PRUEBA DEL FLUJO COMPLETO: CAREER-PLANNER               ")
    print("================================================================================\n")

    try:
        with open('dataset.json', 'r', encoding='utf-8') as f:
            dataset_data = json.load(f)
        skills_list = dataset_data.get('available_skills', [])
        
       
        all_modalities = list(set(c['modality'] for c in dataset_data.get('courses', [])))
        all_difficulties = list(set(c['difficulty'] for c in dataset_data.get('courses', [])))
        
        
        courses_dict = {c['id']: c for c in dataset_data.get('courses', [])}
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'dataset.json' en la raíz.")
        return
    except Exception as e:
        print(f"Error cargando dataset.json: {e}")
        return

    try:
        llm = LLMInterface()
        print(f"-> LLMInterface inicializada con éxito usando el modelo: {llm.model_name}\n")
    except Exception as e:
        print(f"Error al inicializar LLMInterface: {e}")
        return

   
    test_cases = [
        {
            "id": "Caso #1",
            "text": "Quiero aprender machine learning y fronted, cuento con un presupuesto de 500 dolares y 40 dias"
        },
        {
            "id": "Caso #2",
            "text": "Me gustaria aprender backend y programacion orintada a objetos, no me gustan los cursos presenciales, ademas se algo de programacion basica, cuento con 200 dolares y 3 semanas, ademas prefiero la dificultad media baja."
        },
        {
            "id": "Caso #3",
            "text": "quiero aprender a programar en javascipt, aprender tambien de desarrollo web y frontend, cuento con un mes y 500 dolares, solo cursos online."
        },
        {
            "id": "Caso #4",
            "text": "quiero saber inteligencia artificial."
        },
        {
            "id": "Caso #5",
            "text": "Quiero aprender frontend web y cloud computing. Tengo un presupuesto de 500 dólares y 300 horas disponibles. Puedo estudiar online, mixto o presencial, y estoy listo para cualquier nivel de dificultad desde baja hasta alta."
        },
        {
            "id": "Caso #6",
            "text": "Quiero convertirme en Data Scientist. Tengo experiencia previa en Python y Estadística. Mi meta es aprender Machine Learning, Deep Learning y Data Science. Tengo un presupuesto de 5000 dólares y 500 horas disponibles para estudiar, pero solo prefiero cursos presenciales."
        }
    ]

    cases_to_run = test_cases
    if len(sys.argv) > 1:
        try:
            target_idx = int(sys.argv[1]) - 1
            if 0 <= target_idx < len(test_cases):
                cases_to_run = [test_cases[target_idx]]
            else:
                print(f"Error: El ejemplo {sys.argv[1]} no existe. Usa un número del 1 al {len(test_cases)}.")
                return
        except ValueError:
            print(f"Error: El argumento debe ser un número entero (ej: python test_career_planner.py 1).")
            return

    
    for case in cases_to_run:
        print("=" * 80)
        print(f"EJECUTANDO: {case['id']}")
        print(f"Texto del usuario: \"{case['text']}\"")
        print("-" * 80)

        print("[LLM] Extrayendo parámetros del lenguaje natural...")
        
        start_skills = llm.get_start_skill(case['text'], skills_list)
        goal_skills = llm.get_goals_from_text(case['text'], skills_list)
        money = llm.get_money(case['text'])
        time_hours = llm.get_time(case['text'])
        modalities = llm.get_modality(case['text'], all_modalities)
        difficulties = llm.get_difficulty(case['text'], all_difficulties)

        print(f"  > Start Skills (Conocido): {start_skills}")
        print(f"  > Goal Skills (Metas):     {goal_skills}")
        print(f"  > Dinero Máximo ($):       {money if money != 10000000000000 else 'Infinito (Sin restricción)'}")
        print(f"  > Tiempo Máximo (Horas):   {time_hours if time_hours != 10000000000000 else 'Infinito (Sin restricción)'}")
        print(f"  > Modalidades Aceptadas:   {modalities}")
        print(f"  > Dificultades Aceptadas:  {difficulties}\n")

        if not goal_skills:
            print("[Planificador] Cancelado: El LLM no identificó metas académicas válidas en el texto.\n")
            continue

       
        print("[Planificador] Inicializando entorno de planificación adaptativo...")
        planner = Planner(
            start_skills=start_skills,
            goal_skills=goal_skills,
            modalities=modalities,
            difficulties=difficulties,
            money=money,
            time=time_hours
        )

        
        discovered_trajectories = {}

        def print_plan_details(label, plan, status):
            if not plan:
                print(f"  -> {label} no logró encontrar una ruta válida.")
                return

            reconstructed = []
            ids_list = []
            total_money = 0
            total_time = 0

            for item in plan:
                cid = item.get('id') if isinstance(item, dict) else item
                ids_list.append(cid)
                course = courses_dict.get(cid)
                if course:
                    reconstructed.append(course)
                    total_money += course.get('cost', 0)
                    total_time += course.get('duration_hours', 0)

            discovered_trajectories[label] = reconstructed

            print(f"  -> {label} Encontró solución ({status}): {ids_list}")
            print(f"     Cursos en la ruta: {len(reconstructed)}")
            print(f"     Costo total: ${total_money}")
            print(f"     Tiempo total: {total_time} horas")
            for idx, course in enumerate(reconstructed, 1):
                print(
                    f"       {idx}. {course['id']} | Cost: ${course.get('cost', 0)} | Duration: {course.get('duration_hours', 0)}h | "
                    f"Modality: {course.get('modality')} | Difficulty: {course.get('difficulty')}"
                )

      
        print("[Algoritmo] Ejecutando Búsqueda en Anchura (BFS)...")
        res_bfs = planner.run_bfs_planner()
        if isinstance(res_bfs, tuple) and len(res_bfs) == 2:
            status_bfs, plan_bfs = res_bfs
        else:
            plan_bfs = res_bfs
            status_bfs = 'success' if plan_bfs else 'failed'

        print_plan_details("Ruta BFS (Anchura)", plan_bfs if status_bfs in ['success', 'relaxed_success', 'forced_success'] else [], status_bfs)

   
        print("[Algoritmo] Ejecutando Búsqueda de Costo Uniforme (UCS)...")
        res_ucs = planner.run_ucs_planner()
        if isinstance(res_ucs, tuple) and len(res_ucs) == 2:
            status_ucs, plan_ucs = res_ucs
        else:
            plan_ucs = res_ucs
            status_ucs = 'success' if plan_ucs else 'failed'

        print_plan_details("Ruta UCS (Costo)", plan_ucs if status_ucs in ['success', 'relaxed_success', 'forced_success'] else [], status_ucs)

 
        print("[Algoritmo] Ejecutando Búsqueda Heurística A*...")
        res_astar = planner.run_astar_planner()
        if isinstance(res_astar, tuple) and len(res_astar) == 2:
            status_astar, plan_astar = res_astar
        else:
            plan_astar = res_astar
            status_astar = 'success' if plan_astar else 'failed'

        print_plan_details("Ruta A* (Heurística)", plan_astar if status_astar in ['success', 'relaxed_success', 'forced_success'] else [], status_astar)
        
        
        status_adaptive = 'failed'
        adaptive_was_last_resort = False

      
        if not discovered_trajectories:
            print("[Algoritmo] Ningún método estricto encontró ruta; ejecutando Adaptive como respaldo...")
            res_adaptive = planner.run_adaptive_planner()
            if isinstance(res_adaptive, tuple) and len(res_adaptive) == 2:
                status_adaptive, plan_adaptive = res_adaptive
            else:
                plan_adaptive = res_adaptive
                status_adaptive = 'success' if plan_adaptive else 'failed'
                
            print_plan_details("Ruta Adaptive (Respaldo)", plan_adaptive if status_adaptive in ['success', 'relaxed_success', 'forced_success'] else [], status_adaptive)
            adaptive_was_last_resort = status_adaptive in ['success', 'relaxed_success', 'forced_success']

        print()

        if adaptive_was_last_resort and len(discovered_trajectories) == 1 and "Ruta Adaptive (Respaldo)" in discovered_trajectories:
            print("[LLM] Evaluando solución adaptativa (restricciones fueron relajadas)...")
            adaptive_trajectory = discovered_trajectories.get("Ruta Adaptive (Respaldo)", [])
            
            if hasattr(llm, 'evaluate_adaptive_trajectory'):
                adaptive_eval = llm.evaluate_adaptive_trajectory(case['text'], adaptive_trajectory, all_modalities, all_difficulties)
                print("\n================ ANÁLISIS DE SOLUCIÓN ADAPTATIVA ================")
                print("Restricciones que fue necesario relajar:")
                for rel in adaptive_eval.get('restricciones_relajadas', []):
                    print(f"  • {rel.get('restriccion')}")
                    print(f"    - Solicitado: {rel.get('solicitado')}")
                    print(f"    - Ofrecido: {rel.get('ofrecido')}")
                    print(f"    - Razón: {rel.get('razon')}")
                
                print("\nAspectos positivos de esta ruta alternativa:")
                for asp in adaptive_eval.get('aspectos_positivos', []):
                    print(f"  ✓ {asp}")
                
                print(f"\nJustificación pedagógica:")
                print(f"  {adaptive_eval.get('justificacion_general', 'Sin justificación disponible.')}")
                print("================================================================\n")
            else:
                print("  -> Nota: 'evaluate_adaptive_trajectory' no está en LLMInterface, procediendo a auditoría estándar.")
      
                audit_result = llm.compare_and_evaluate_trajectories(case['text'], discovered_trajectories)
                print_audit_results(audit_result)
            continue

        if not discovered_trajectories:
            print("[Auditoría LLM] No se generó ninguna trayectoria válida por los algoritmos para auditar.\n")
            continue

        print("[LLM] Enviando todas las trayectorias descubiertas para Evaluación y Selección Cualitativa...")
        audit_result = llm.compare_and_evaluate_trajectories(case['text'], discovered_trajectories)
        print_audit_results(audit_result)
        
      
        time.sleep(2)

def print_audit_results(audit_result):
    print("\n================ VERDICTO DEL JUEZ (LLM) ================")
    print(f"Trayectoria más alineada: {audit_result.get('recommended_trajectory_name', 'No determinado')}")
    print("Ranking General de Soluciones:")
    for idx, item in enumerate(audit_result.get('ranking', []), 1):
        print(f"  {idx}. {item.get('name')} | Puntuación Cualitativa: {item.get('score')}/100")
        print(f"     [+] Pros: {item.get('pros')}")
        print(f"     [-] Contras: {item.get('cons')}")
    print(f"\nConclusión final:\n{audit_result.get('final_conclusion', 'Sin conclusión disponible.')}\n")
    print("============================================================\n")

if __name__ == "__main__":
    run_pipeline_test()