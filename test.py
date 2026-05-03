from planner import Planner
from llm_interface import LLMInterface
import os
from pathlib import Path


def load_env_file(env_path='.env'):
    path = Path(env_path)
    if not path.exists():
        return

    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

def test_my_planner(student_goal, mode='bfs'):
    my_app = Planner()
    initial_knowledge = []
    
    print(f"Iniciando búsqueda para: {student_goal} (modo={mode})")
    
    if mode == 'bfs':
        result_plan = my_app.run_bfs_planner(initial_knowledge, student_goal)
    elif mode == 'cost':
        result_plan = my_app.run_cost_planner(initial_knowledge, student_goal)
    else:
        raise ValueError(f"Modo de planner desconocido: {mode}")

    if result_plan:
        print("¡Plan encontrado!")
        for i, course_id in enumerate(result_plan, 1):
            print(f"{i}. Tomar: {course_id}")
    else:
        print("❌ No se encontró un camino válido.")
    return result_plan


def test_extraction():
    load_env_file()

    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        raise RuntimeError("Falta la variable de entorno GEMINI_API_KEY. Crea un archivo .env con esa clave.")

    llm = LLMInterface(API_KEY)
    planner = Planner()
    
    my_skills_list = [
        "programacion_basica", "logica_matematica", "estructuras_datos", 
        "algoritmos_avanzados", "bases_de_datos", "redes_computadoras", 
        "arquitectura_sistemas", "inteligencia_artificial", "desarrollo_web", 
        "seguridad_informatica"
    ]

    test_prompts = [
        "Quiero ser experto en desarrollo web" 
    ]

    print("Iniciando pruebas de extracción")

    # for text in test_prompts:
    #     print(f"\nUsuario dice: '{text}'")
    #     goals = llm.get_goals_from_text(text, my_skills_list)
    #     print(f"LLM extrajo: {goals} (Tipo: {type(goals)})")

    goals = ["desarrollo_web"]
    
    # Ejecutar y comparar ambos planners: BFS (primera solución) y optimizado por coste
    plans_bfs = test_my_planner(goals, mode='bfs')
    plans_cost = test_my_planner(goals, mode='cost')

    if plans_cost:
        print("\nPlan optimizado por coste:")
        for i, cid in enumerate(plans_cost, 1):
            print(f"{i}. {cid}")

    # if plans_bfs:
    #     # Usamos los datos completos del JSON que tiene el planner para explicar la ruta
    #     explain = llm.explain_plan(plans_bfs, planner.data['courses'])
    #     print("\n--- Explicación del IA (BFS) ---")
    #     print(explain)

if __name__ == "__main__":
    goals = test_extraction()

