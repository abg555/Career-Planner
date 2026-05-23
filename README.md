# Career-Planner

Proyecto: Planificación de trayectoria profesional (TFG/Proyecto Final)

Descripción breve

Este proyecto construye rutas formativas (secuencias de cursos) para alcanzar objetivos profesionales descritos en lenguaje natural. Usa un componente LLM para extraer metas y restricciones y un planificador STRIPS con variantes BFS/UCS/A\* y un planner adaptativo.

Requisitos

- Python 3.8+
- Dependencias (instalar con `pip install -r requirements.txt`)

Instrucciones de ejecución

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Ejecutar la interfaz interactiva:

```bash
python main.py
```

3. Ejecutar los casos de ejemplo del pipeline:

```bash
python test_career_planner.py
```

4. Ejecutar tests unitarios (si los hay):

```bash
pytest -q
```

Configuración del uso del LLM

El proyecto espera una variable de entorno `API_KEY` con la clave del proveedor del LLM. Por defecto `LLMInterface` usa `base_url="https://api.groq.com/openai/v1"` y `model_name` por defecto (ajustable en `LLMInterface`).

Cómo obtener una API key (Groq Console)

1. Regístrate en el panel del proveedor LLM (Groq Console).
2. En el panel busca "API Keys" o "Create API Key" y genera una nueva clave.
3. Copia la clave.
4. Crea un archivo `.env` en la raíz del proyecto y añade:

```
API_KEY=tu_clave_copiada_aqui
```

Alternativa temporal (sesión de terminal):

- PowerShell (sesión actual):

```powershell
$env:API_KEY = "su_clave_aqui"
python test_career_planner.py
```

- Unix / macOS (sesión actual):

```bash
export API_KEY="su_clave_aqui"
python test_career_planner.py
```

Estructura del repositorio

- `llm_interface.py` — wrappers y prompts para el LLM.
- `planner.py` — implementación del planificador (BFS/UCS/A\*/Adaptive).
- `main.py` — interfaz interactiva.
- `test_career_planner.py` — script de pruebas de pipeline con casos ejemplo.
- `dataset.json` — datos de cursos y skills.
