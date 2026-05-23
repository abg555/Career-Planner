import os
import json
import time
from dotenv import load_dotenv
from llm_interface import LLMInterface
from planner import Planner
from test_career_planner import print_audit_results

load_dotenv()

def interactive_main():
    print("================================================================================")
    print("                 CAREER-PLANNER: INTERFAZ INTERACTIVA DE CONSOLA                ")
    print("================================================================================\n")

    # 1. Cargar las habilidades, modalidades y dificultades disponibles desde el dataset
    try:
        with open('dataset.json', 'r', encoding='utf-8') as f:
            dataset_data = json.load(f)
        skills_list = dataset_data.get('available_skills', [])
        
        all_modalities = list(set(c['modality'] for c in dataset_data.get('courses', [])))
        all_difficulties = list(set(c['difficulty'] for c in dataset_data.get('courses', [])))
        courses_dict = {c['id']: c for c in dataset_data.get('courses', [])}
        print("-> Catálogos y dataset cargados correctamente.")
    except FileNotFoundError:
        print("Error Crítico: No se encontró el archivo 'dataset.json' en la raíz.")
        return
    except Exception as e:
        print(f"Error cargando dataset.json: {e}")
        return

    # 2. Inicializar la interfaz del LLM
    try:
        llm = LLMInterface()
        print(f"-> LLMInterface lista con el modelo: {llm.model_name}\n")
    except Exception as e:
        print(f"Error al inicializar LLMInterface: {e}")
        return

    print("Bienvenido al planificador de trayectorias profesionales basado en Inteligencia Artificial.")
    print("Escribe tus metas, presupuesto, tiempo o modalidad en lenguaje natural.")
    print("Escribe 'salir' o 'exit' para finalizar el programa.\n")

    # Bucle interactivo por consola
    while True:
        print("-" * 80)
        user_input = input("¿Qué perfil educativo deseas planificar hoy?\n>>> ").strip()
        print("-" * 80)

        # Criterio de salida del bucle interactivo
        if user_input.lower() in ['salir', 'exit', 'quit']:
            print("\n¡Gracias por utilizar Career-Planner! Finalizando entorno interactivo...")
            break

        if not user_input:
            print("Entrada vacía. Por favor, describe tus metas educativas.")
            continue

        print("\n[LLM] Extrayendo parámetros del lenguaje natural...")
        start_skills = llm.get_start_skill(user_input, skills_list)
        goal_skills = llm.get_goals_from_text(user_input, skills_list)
        money = llm.get_money(user_input)
        time_hours = llm.get_time(user_input)
        modalities = llm.get_modality(user_input, all_modalities)
        difficulties = llm.get_difficulty(user_input, all_difficulties)

        print(f"  > Start Skills (Conocido): {start_skills}")
        print(f"  > Goal Skills (Metas):     {goal_skills}")
        print(f"  > Dinero Máximo ($):       {money if money != 10000000000000 else 'Infinito (Sin restricción)'}")
        print(f"  > Tiempo Máximo (Horas):   {time_hours if time_hours != 10000000000000 else 'Infinito (Sin restricción)'}")
        print(f"  > Modalidades Aceptadas:   {modalities}")
        print(f"  > Dificultades Aceptadas:  {difficulties}\n")

        if not goal_skills:
            print("[Planificador] Cancelado: El LLM no identificó objetivos educativos válidos en tu entrada.")
            print("Prueba siendo más explícito (ej: 'Quiero aprender desarrollo web o machine learning').\n")
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

   
        def print_and_track_plan_details(label, plan, status):
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

        # Probar Búsqueda en Anchura (BFS)
        print("[Algoritmo] Ejecutando Búsqueda en Anchura (BFS)...")
        res_bfs = planner.run_bfs_planner()
        if isinstance(res_bfs, tuple) and len(res_bfs) == 2:
            status_bfs, plan_bfs = res_bfs
        else:
            plan_bfs = res_bfs
            status_bfs = 'success' if plan_bfs else 'failed'
        print_and_track_plan_details("Ruta BFS (Anchura)", plan_bfs if status_bfs in ['success', 'relaxed_success', 'forced_success'] else [], status_bfs)

        # Probar Búsqueda por Costo (UCS / Uniform Cost)
        print("[Algoritmo] Ejecutando Búsqueda de Costo Uniforme (UCS)...")
        res_ucs = planner.run_ucs_planner()
        if isinstance(res_ucs, tuple) and len(res_ucs) == 2:
            status_ucs, plan_ucs = res_ucs
        else:
            plan_ucs = res_ucs
            status_ucs = 'success' if plan_ucs else 'failed'
        print_and_track_plan_details("Ruta UCS (Costo)", plan_ucs if status_ucs in ['success', 'relaxed_success', 'forced_success'] else [], status_ucs)

        # Probar Búsqueda Heurística A* directamente
        print("[Algoritmo] Ejecutando Búsqueda Heurística A*...")
        res_astar = planner.run_astar_planner()
        if isinstance(res_astar, tuple) and len(res_astar) == 2:
            status_astar, plan_astar = res_astar
        else:
            plan_astar = res_astar
            status_astar = 'success' if plan_astar else 'failed'
        print_and_track_plan_details("Ruta A* (Heurística)", plan_astar if status_astar in ['success', 'relaxed_success', 'forced_success'] else [], status_astar)
        
        
        status_adaptive = 'failed'
        adaptive_was_last_resort = False

        # Adaptive solo como respaldo si no hubo ninguna trayectoria estricta válida
        if not discovered_trajectories:
            print("[Algoritmo] Ningún método estricto encontró ruta; ejecutando Adaptive como respaldo...")
            res_adaptive = planner.run_adaptive_planner()
            if isinstance(res_adaptive, tuple) and len(res_adaptive) == 2:
                status_adaptive, plan_adaptive = res_adaptive
            else:
                plan_adaptive = res_adaptive
                status_adaptive = 'success' if plan_adaptive else 'failed'
                
            print_and_track_plan_details("Ruta Adaptive (Respaldo)", plan_adaptive if status_adaptive in ['success', 'relaxed_success', 'forced_success'] else [], status_adaptive)
            adaptive_was_last_resort = status_adaptive in ['success', 'relaxed_success', 'forced_success']

        print()

       
        if not discovered_trajectories:
            print("[Auditoría LLM] No se generó ninguna trayectoria válida por los algoritmos para auditar.\n")
            continue

        if adaptive_was_last_resort and len(discovered_trajectories) == 1 and "Ruta Adaptive (Respaldo)" in discovered_trajectories:
            print("[LLM] Evaluando solución adaptativa (restricciones fueron relajadas)...")
            adaptive_trajectory = discovered_trajectories.get("Ruta Adaptive (Respaldo)", [])
            
            if hasattr(llm, 'evaluate_adaptive_trajectory'):
                adaptive_eval = llm.evaluate_adaptive_trajectory(user_input, adaptive_trajectory, all_modalities, all_difficulties)
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
                audit_result = llm.compare_and_evaluate_trajectories(user_input, discovered_trajectories)
                print_audit_results(audit_result)
        else:
          
            print("[LLM] Enviando todas las trayectorias descubiertas para Evaluación y Selección Cualitativa...")
            audit_result = llm.compare_and_evaluate_trajectories(user_input, discovered_trajectories)
            print_audit_results(audit_result)

     
        time.sleep(1)

if __name__ == "__main__":
    interactive_main()