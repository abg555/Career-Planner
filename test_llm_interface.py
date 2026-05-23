import json
from pprint import pprint
from llm_interface import LLMInterface
import os
import time
import sys


def load_dataset(path='dataset.json'):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    modalities = []
    difficulties = []
    skills = data.get('available_skills', [])
    for c in data.get('courses', []):
        m = c.get('modality')
        d = c.get('difficulty')
        if m and m not in modalities:
            modalities.append(m)
        if d and d not in difficulties:
            difficulties.append(d)
    return skills, modalities, difficulties


EXAMPLES = [
    "Quiero ser experto en inteligencia artificial, solo con cursos online, con un presupuesto de 100 dolares y en solo 3 meses",
    "Me interesa desarrollo web pero ya conozco bases de datos. Puedo invertir 50 y prefiero presencial",                    
    "No sé nada, quiero empezar desde cero y aprender programación, tengo  6 meses",                 
    "Quiero trabajar en backend y se algo de programacion, prefiero cursos donde puede ir presecial pero tambien pueda quedame en la casa y dispongo de 200 dólares y 1 mes",                            
    "Tengo experiencia en python y sql, pero quiero machine learning, solo online, presupuesto 400 dolares y prefiero curso de alta dificultad", 
    "Quiero aprender estadisticas y se algo de estructura de datos, no me importa modalidad, tiempo 2 semanas",                         
    "Busco aprender deep learning pero solo si es presencial y avanzado, presupuesto 80, tiempo 4 meses",                  
    "Me gustaría aprender data cience y estadistica; puedo pagar 30 dolares y tengo 90 dias",                                     
    "Quiero ser programador web, soy principiante, tengo 99 dolares y puedo dedicar 120 horas",                            
    "Mi meta es seguridad informatica, prefiero presencial o online ya que no me gustan los cursos mixtos, presupuesto 25, plazo 15 dias, y no quiero que sean cursos de alta dificultad",
    "Me gustaria aprender backend y programacion orintada a objetos, no me gustan los cursos presenciales, ademas se algo de programacion basica, cuento con 200 dolares y 3 semanas, ademas prefiero la dificultad media baja.",              
    "quiero aprender a programar en javascipt, aprender tambien de programacion web y frontend, cuento con un mes y 500 dolares, solo cursos online.",
]


def run_tests():
    skills, modalities, difficulties = load_dataset()
    print('Dataset modalities:', modalities)
    print('Dataset difficulties:', difficulties)
    print('Available skills count:', len(skills))

    llm = LLMInterface()

   
    indices_a_probar = range(len(EXAMPLES))  

   
    if len(sys.argv) > 1:
        try:
            target_idx = int(sys.argv[1]) - 1 
            if 0 <= target_idx < len(EXAMPLES):
                indices_a_probar = [target_idx]
            else:
                print(f"Error: El ejemplo {sys.argv[1]} no existe. Usa un número del 1 al {len(EXAMPLES)}.")
                return
        except ValueError:
            print("Error: El argumento debe ser un número entero (ej: python test_llm_interface.py 8).")
            return
    

    for idx in indices_a_probar:
        text = EXAMPLES[idx]
        print('\n' + '=' * 80)
        print(f'Example #{idx + 1}:')
        print(text)
        print('-' * 40)
        
        goals = llm.get_goals_from_text(text, skills)
        time.sleep(0.5) 
        
        starts = llm.get_start_skill(text, skills)
        time.sleep(0.5)
        
        money = llm.get_money(text)
        time.sleep(0.5)
        
        time_h = llm.get_time(text)
        time.sleep(0.5)
        
        mods = llm.get_modality(text, modalities)
        time.sleep(0.5)
        
        diffs = llm.get_difficulty(text, difficulties)

        pprint({
            'goals_extracted': goals,
            'start_skills_extracted': starts,
            'money_extracted': money,
            'time_hours_extracted': time_h,
            'modalities_extracted': mods,
            'difficulties_extracted': diffs,
        })


if __name__ == '__main__':
    run_tests()