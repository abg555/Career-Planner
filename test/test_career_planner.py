import os
import json
import time
import sys
from dotenv import load_dotenv

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
            "text": "Me gustaria aprender a programar en python y en javascript, no quiero cursos de dificultad alta cuento con 500 dolares y un mes"
        },
        {
            "id": "Caso #2",
            "text": "Me gustaria dedicarme a las base de datos y programar en sql, cuento con 250 dolares y 3 semanas."
        },
        {
            "id": "Caso #3",
            "text": "Quiero dedicarme al desarrollo web, tanto frontend como backend, solo quiero hacer cursos online con dificultat media o baja, tengo de presupuesto 300 dolares y 2 meses."
        },
        {
            "id": "Caso #4",
            "text": "Quiero estudiar clud computing y devops, conozco algo de programacion, no me gustan los cursos mixtos ni los cursos de dificultad alta, tengo un tiempo limite de 10 semanas."
        },
        {
            "id": "Caso #5",
            "text": "Quiero aprender programacion orientada a objetos Solo cursos de dificultad media y solo cursos onlinen o presencial, cuento con 200 dolares y 3 semanas."
        },
        {
            "id": "Caso #6",
            "text": "Quuiero apender devops, se algo de control de versiones. Cuento con 250 dolares y 1 mes."
        },
        {
            "id": "Caso #7",
            "text": "Quiero dedicarme a la ciencia de datos, se programar en python pero nada mas"
        },
        {
           "id": "Caso #8",
            "text":"Quiero ser experto en inteligencia artificial"
        },
        {
            "id": "Caso #9",
            "text":"Quiero aprender control de versiones solo cursos mixtos"
        },
        {
            "id": "Caso #10",
            "text": "Quiero aprender a programar en javascript, solo cursos de alta dificultad"
        },
        {
            "id": "Caso #11",
            "text": "Quiero quiero aprender redes de computadoras, cuento con solo 30 dolares"
        },
        {
            "id": "Caso #12",
            "text": "Me gustaria saber criptografia, ya he tomado cursos de logica y de ciberseguridad, quiero hacerlo en solo 2 dias"
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

        # Diccionario intermedio para capturar las trayectorias brutas por separado
        raw_algorithms_results = {}

        def track_raw_algorithm_output(label, plan, status):
            """Guarda temporalmente la ruta sin imprimir repetidos directamente."""
            if plan and status in ['success', 'relaxed_success', 'forced_success']:
                reconstructed = []
                for item in plan:
                    cid = item.get('id') if isinstance(item, dict) else item
                    course = courses_dict.get(cid)
                    if course:
                        reconstructed.append(course)
                
                if reconstructed:
                    raw_algorithms_results[label] = reconstructed

        # --- EJECUCIÓN DE MÉTODOS ESTRICTOS ---
        print("[Algoritmo] Ejecutando Búsqueda en Anchura (BFS)...")
        res_bfs,_ = planner.run_bfs_planner()
        status_bfs = res_bfs[0] if isinstance(res_bfs, tuple) and len(res_bfs) == 2 else ('success' if res_bfs else 'failed')
        plan_bfs = res_bfs[1] if isinstance(res_bfs, tuple) and len(res_bfs) == 2 else res_bfs
        track_raw_algorithm_output("Ruta BFS (Anchura)", plan_bfs, status_bfs)

        print("[Algoritmo] Ejecutando Búsqueda de Costo Uniforme (UCS)...")
        res_ucs,_ = planner.run_ucs_planner()
        status_ucs = res_ucs[0] if isinstance(res_ucs, tuple) and len(res_ucs) == 2 else ('success' if res_ucs else 'failed')
        plan_ucs = res_ucs[1] if isinstance(res_ucs, tuple) and len(res_ucs) == 2 else res_ucs
        track_raw_algorithm_output("Ruta UCS (Costo)", plan_ucs, status_ucs)

        print("[Algoritmo] Ejecutando Búsqueda Heurística A*...")
        res_astar,_ = planner.run_astar_planner()
        status_astar = res_astar[0] if isinstance(res_astar, tuple) and len(res_astar) == 2 else ('success' if res_astar else 'failed')
        plan_astar = res_astar[1] if isinstance(res_astar, tuple) and len(res_astar) == 2 else res_astar
        track_raw_algorithm_output("Ruta A* (Heurística)", plan_astar, status_astar)
        
        # --- RESPALDO ADAPTATIVO SI TODO LO ANTERIOR FALLÓ ---
        status_adaptive = 'failed'
        adaptive_was_last_resort = False

        if not raw_algorithms_results:
            print("[Algoritmo] Ningún método estricto encontró ruta; ejecutando Adaptive como respaldo...")
            res_adaptive = planner.run_adaptive_planner()
            status_adaptive = res_adaptive[0] if isinstance(res_adaptive, tuple) and len(res_adaptive) == 2 else ('success' if res_adaptive else 'failed')
            plan_adaptive = res_adaptive[1] if isinstance(res_adaptive, tuple) and len(res_adaptive) == 2 else res_adaptive
            track_raw_algorithm_output("Ruta Adaptive (Respaldo)", plan_adaptive, status_adaptive)
            adaptive_was_last_resort = len(raw_algorithms_results) > 0

        # =========================================================================
        # UNIFICACIÓN DE RUTAS IDÉNTICAS (IGUAL QUE EN LA INTERFAZ / GUI)
        # =========================================================================
        discovered_trajectories = {}
        inverse_trajectory_map = {}

        for algo_label, courses in raw_algorithms_results.items():
            tuple_ids = tuple(c['id'] for c in courses)
            if tuple_ids not in inverse_trajectory_map:
                inverse_trajectory_map[tuple_ids] = {
                    "names": [],
                    "courses": courses
                }
            inverse_trajectory_map[tuple_ids]["names"].append(algo_label)

        # Mapear claves unificadas usando barras diagonales
        for tuple_ids, info in inverse_trajectory_map.items():
            combined_label = "/".join(info["names"])
            discovered_trajectories[combined_label] = info["courses"]

        # --- MOSTRAR LAS TRAYECTORIAS CONSOLIDADAS EN CONSOLA ---
        print("\n================ TRAYECTORIAS UNIFICADAS ENCONTRADAS ================")
        if not discovered_trajectories:
            print("[Auditoría LLM] No se generó ninguna trayectoria válida por los algoritmos para auditar.\n")
            continue
        else:
            for label, reconstructed in discovered_trajectories.items():
                total_money = sum(c.get('cost', 0) for c in reconstructed)
                total_time = sum(c.get('duration_hours', 0) for c in reconstructed)
                ids_list = [c['id'] for c in reconstructed]
                
                print(f"\n-> {label} Encontró solución:")
                print(f"     Cursos en la ruta: {len(reconstructed)}")
                print(f"     Costo total: ${total_money}")
                print(f"     Tiempo total: {total_time} horas")
                for idx, course in enumerate(reconstructed, 1):
                    print(
                        f"       {idx}. {course['id']} | Cost: ${course.get('cost', 0)} | Duration: {course.get('duration_hours', 0)}h | "
                        f"Modality: {course.get('modality')} | Difficulty: {course.get('difficulty')}"
                    )
        print("=====================================================================\n")

        # =========================================================================
        # COORDINACIÓN DE AUDITORÍA FINAL DEL CASO
        # =========================================================================
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
                
                # SE ELIMINÓ EL BUCLE DE ASPECTOS POSITIVOS EN PLECAS AQUÍ
                
                print(f"\nAnálisis pedagógico y beneficios de la ruta:")
                print(f"  {adaptive_eval.get('justificacion_general', 'Sin análisis disponible.')}")
                print("================================================================\n")
            else:
                print("  -> Nota: 'evaluate_adaptive_trajectory' no está en LLMInterface, procediendo a auditoría estándar.")
                audit_result = llm.compare_and_evaluate_trajectories(case['text'], discovered_trajectories)
                print_audit_results(audit_result)
        else:
            print("[LLM] Enviando todas las trayectorias descubiertas para Evaluación y Selección Cualitativa...")
            audit_result = llm.compare_and_evaluate_trajectories(case['text'], discovered_trajectories)
            print_audit_results(audit_result)
            
        time.sleep(2)

def print_audit_results(audit_result):
    print("================ VERDICTO DEL JUEZ (LLM) ================")
    if not audit_result:
        print("El resultado de la auditoría está vacío (None).")
        return
    
    import re
    
    def limpiar_html_para_consola(texto_html):
        if not texto_html:
            return ""
        txt = texto_html.replace("<li>", "\n  • ").replace("</li>", "")
        txt = txt.replace("<ul>", "").replace("</ul>", "")
        txt = txt.replace("<br>", "\n").replace("<br><br>", "\n\n")
        txt = re.sub(r'<[^>]+>', '', txt)
        return txt.strip()
        
    print("\n[ANÁLISIS DETALLADO DE ALTERNATIVAS]:")
    analisis_limpio = limpiar_html_para_consola(audit_result.get('analisis_detallado_alternativas'))
    print(analisis_limpio)
    
    print("\n[GUÍA DE ORIENTACIÓN Y TRADE-OFFS]:")
    guia_limpia = limpiar_html_para_consola(audit_result.get('guia_orientacion_usuario'))
    print(guia_limpia)
    print("=========================================================")

if __name__ == "__main__":
    run_pipeline_test()