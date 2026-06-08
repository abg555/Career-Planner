# Career-Planner

Proyecto: Planificación de trayectoria profesional mediante IA y Algoritmos de Búsqueda Formal

## Descripción breve

Este proyecto construye rutas formativas personalizadas (secuencias de cursos) para alcanzar objetivos profesionales descritos por el usuario en lenguaje natural. El sistema combina un componente de Procesamiento de Lenguaje Natural (NLP) asistido por un LLM para la extracción de metas y restricciones, con un planificador formal bajo el paradigma **STRIPS** que ejecuta variantes de búsqueda implícita (`BFS`, `UCS`, `A*`) y un motor de planificación adaptativo para escenarios con restricciones estrictas.

## Requisitos del Sistema

- **Python 3.8 o superior**
- Las dependencias externas especificadas en el archivo requirements.tx

## El Dataset del Dominio

El sistema opera sobre un dataset en formato estructurado (`JSON`) enfocado en el campo de las **Ciencias de la Computación**. Este archivo actúa como la base de conocimiento o grafo de dependencias que modela las interacciones lógicas de un entorno educativo y técnico real.

La información se compone de tres bloques fundamentales:

1. **Campos de Control Lógico:** El archivo define de manera global el dominio (`Ciencias de la Computación`) y el eje conceptual del proyecto (`Planificación de trayectoria profesional`).
2. **Catálogo Global de Habilidades (`available_skills`):** Un listado exhaustivo de competencias técnicas que un estudiante puede adquirir o requerir en el mercado. Contiene un total de 30 competencias core, tales como:
   - **Bases de la programación:** `programacion_basica`, `python_programming`, `estructuras_datos`.
   - **Especialidades avanzadas:** `inteligencia_artificial`, `machine_learning`, `deep_learning`, `data_science`.
   - **Ingeniería de software e Infraestructura:** `arquitectura_sistemas`, `cloud_computing`, `devops`, `software_testing`, `ui_ux`.
3. **Catálogo de Operadores Académicos (`courses`):** Un conjunto de cursos y entrenamientos que actúan como funciones de transición en el planificador (operadores STRIPS), los cuales modifican el estado de conocimientos del usuario.

Cada elemento dentro de la lista de cursos contiene atributos cuantitativos y cualitativos estrictos que definen el peso y las aristas del grafo de búsqueda:

| Atributo         | Tipo           | Descripción                                                                       |
| :--------------- | :------------- | :-------------------------------------------------------------------------------- |
| `id`             | `string`       | Identificador único del curso en el sistema.                                      |
| `title`          | `string`       | Nombre legible y comercial del curso.                                             |
| `description`    | `string`       | Resumen conceptual de las temáticas abordadas en el temario.                      |
| `prerequisites`  | `list[string]` | **Precondiciones (Alpha):** Habilidades necesarias antes de poder inscribirse.    |
| `effects`        | `list[string]` | **Lista de Adición (Gamma):** Habilidades que se añaden al estado al completarlo. |
| `cost`           | `int`          | Coste monetario del curso expresado en USD.                                       |
| `duration_hours` | `int`          | Horas aproximadas de dedicación total requeridas.                                 |
| `difficulty`     | `string`       | Nivel de complejidad computacional relativo (`baja`, `media`, `alta`).            |
| `modality`       | `string`       | Formato principal de impartición (`online`, `presencial`, `mixto`).               |

## Tipos de Consultas Soportadas

Los usuarios pueden estructurar sus solicitudes con total flexibilidad temática e indicar explícitamente sus condiciones operativas de presupuesto, tiempo disponible, modalidades de estudio deseadas y límites de dificultad académica.

A continuación se detallan ejemplos reales del tipo de consultas que el pipeline procesa:

- **Orientación hacia Inteligencia Artificial:** > _"Quiero ser experto en inteligencia artificial, solo con cursos online, con un presupuesto de 100 dólares y en solo 3 meses"._
- **Orientación a Desarrollo Web con Conocimiento Previo:** > _"Me interesa desarrollo web pero ya conozco bases de datos. Puedo invertir 50 y prefiero presencial"._
- **Iniciación desde Cero Absoluto:** > _"No sé nada, quiero empezar desde cero y aprender programación, tengo 6 meses"._

Cuando un usuario define un perfil de búsqueda con restricciones excesivamente estrictas, los algoritmos clásicos de búsqueda formal (`BFS`, `UCS`, `A*`) pueden fallar al no encontrar ningún camino válido en el grafo que cumpla el 100% de los parámetros aplicados (por ejemplo, querer aprender IA Avanzada en modalidad presencial con $0 USD de presupuesto).

Para evitar respuestas vacías y bloqueos en el sistema, se dispara el **Modo Adaptativo**.

## Configuración del Uso del LLM (Groq Cloud)

El componente de procesamiento de lenguaje natural e interpretación adaptativa (`llm_interface.py`) delega la inferencia de IA a la infraestructura de **Groq Console** debido a sus altísimas tasas de velocidad en la generación de tokens estructurados.

**Parámetros del Entorno**

- Endpoint de Conexión: `https://api.groq.com/openai/v1`.
- Modelo Utilizado: `llama-3.3-70b-versatile` (Configurado internamente con una temperatura baja de `0.1` para mitigar alucinaciones y forzar respuestas sintácticas consistentes bajo esquemas estrictos de JSON).

**Nota Importante sobre las Cuotas de la API:** Las cuentas de desarrollador gratuitas en Groq Console poseen una **cuota de peticiones relativamente pequeña** (límites estrictos de _Tokens Por Minuto - TPM_ y _Solicitudes Por Día - RPD_). Por este motivo, si se ejecutan de manera masiva o consecutiva los pipelines de integración completos (`test_career_planner.py` o `test_llm_interface.py`), es muy probable encontrarse con un error de tipo `RateLimitError (HTTP 429)`. Se recomienda encarecidamente utilizar la ejecución parametrizada para probar los casos de estudio uno por uno (ej. `python test/test_planner.py 1`) para evitar saturar la cuota contratada.

**Paso a Paso para la Integración de la API Key:**

Para que la aplicación pueda conectarse al modelo y extraer las metas de los usuarios, es obligatorio proveer una credencial de acceso válida:

1. **Obtener la API Key:**
   - Ingrese al panel de control en [Groq Cloud Console](https://console.groq.com/).
   - En el menú de navegación lateral izquierdo, seleccione la sección **"API Keys"**.
   - Haga clic en el botón **"Create API Key"**, asigne un nombre identificador para su control local y copie la cadena de texto generada (comienza habitualmente con el prefijo `gsk_`).

2. **Inyección por Archivo de Entorno Local (Recomendado):**
   Cree un archivo de texto plano con el nombre exacto `.env` en la raíz del proyecto (en el mismo directorio donde residen `main.py` y `gui.py`) y declare su clave de la siguiente forma:
   ```env
   API_KEY=gsk_tu_clave_real_de_groq_aqui
   ```

## Instrucciones de Ejecución

Para desplegar y probar los diferentes módulos del proyecto, siga estos pasos en su terminal:

1. **Instalar las dependencias externas:**
   Antes de iniciar la ejecucion del sistema se debe instalar los paquetes requeridos utilizando el gestor de paquetes de Python (`pip`):
   ```bash
   pip install -r requirements.txt
   ```
2. **Ejecutar el Archivo Principal (Interfaz Interactiva de Consola):**
   Es el punto de entrada principal del proyecto. Le permite al usuario escribir su meta profesional en lenguaje natural y el sistema se encarga automáticamente de ejecutar la extracción de objetivos, la ejecución de los algoritmos de búsqueda formal y la evaluación cualitativa de las rutas propuestas por estos mismos.

   ```bash
   python main.py
   ```

3. **Ejecutar la Interfaz Gráfica de Usuario (GUI):**
   Cumple exactamente con la misma función que el archivo principal (`main.py`), pero proporciona una interfaz visual desarrollada en PyQt5 para facilitar la visualización del flujo del sistema:

   ```bash
   python gui.py
   ```

   **Nota:** Para conocer en profundidad todas las capacidades de control, componentes lógicos y el funcionamiento detallado de esta interfaz visual, dispone de un manual de usuario en el archivo manual_usuario.pdf

4. **Ejecutar Pruebas Unitarias de Extracción del LLM:**
   Este script está diseñado exclusivamente para evaluar el comportamiento aislado del componente de Inteligencia Artificial. Se encarga de auditar la precisión del LLM al extraer habilidades iniciales, objetivos finales, presupuestos, límites de tiempo y modalidades a partir de lenguaje natural sin interactuar con los algoritmos del planificador. Cuenta con conjunto de 12 casos de prueba distintos. Puede ejecutar todos los casos en bloque o filtrar para probar un único caso específico pasando su número como argumento:

   ```bash
   # Ejecutar todos los casos de prueba del planificador
   python test/test_llm_interface.py

   # Ejecutar únicamente el caso de estudio #1
   python test/test_llm_interface.py 1
   ```

5. **Ejecutar el Pipeline de Métricas y Validación Algorítmica:**
   Para validar y comparar el rendimiento empírico de las tres variantes de búsqueda (`BFS` vs `UCS` vs `A*`) junto con el comportamiento de la lógica adaptativa ante casos de prueba controlados se uso el script test_planner.py ubicado en la carpeta test.
   Este script cuenta con un total de 14 casos de prueba estructurados (divididos en un grupo de 10 casos para los algoritmos base y un grupo de 4 casos para evaluar la lógica Adaptativa). Puede ejecutar todos los casos en bloque o filtrar para probar un único caso específico pasando su número como argumento:

   ```bash
   # Ejecutar todos los casos de prueba del planificador
   python test/test_planner.py

   # Ejecutar únicamente el caso de estudio #1
   python test/test_planner.py 1
   ```

6. **Ejecutar el Pipeline de Pruebas de Integración con el LLM:**
   Valida el flujo completo de la aplicación uniendo el procesamiento de lenguaje natural, el motor de planificación y los métodos de evaluación calidad de las trayectorias propuestas. Evalúa de forma integral la consistencia de las consultas, el parseo de texto y las respuestas estructuradas definitivas bajo 12 escenarios de prueba complejos, que incluyen tanto casos para los algoritmos de busqueda base y casos para evaluar la ruta adptativa. Pueden ejecutar todos los casos en bloque o filtrar para probar un único caso específico pasando su número como argumento:

   ```bash
   # Ejecutar todos los casos de prueba del planificador
   python test/test_career_planner.py

   # Ejecutar únicamente el caso de estudio #1
   python test/test_career_planner.py 1
   ```

   **Nota de Arquitectura (Componentes del Sistema):**
   El backend de la aplicación se distribuye de manera modular en tres scripts principales que dividen las responsabilidades del sistema:
   - **`planner.py` (Motor de Planificación):** Es el corazón algorítmico. Modela el catálogo de cursos bajo el formalismo **STRIPS** (operadores con precondiciones y efectos) y aloja las tres variantes de búsqueda (`BFS`, `UCS`, `A*`), así como la lógica adaptativa de relajación de restricciones.
   - **`llm_interface.py` (Orquestador de IA):** Sirve de puente con los modelos de lenguaje. Se encarga de la _ingesta_ (extraer las metas y restricciones del texto plano) y de la _evaluación_ (actuar como juez pedagógico para justificar cualitativamente las rutas propuestas).
   - **`metrics.py` (Infraestructura de Medición):** Implementa la clase `SearchMetrics` encargada de auditar de forma aislada la telemetría de los algoritmos (tiempo de ejecución en milisegundos, nodos expandidos y longitud de la ruta).
