import time 

class SearchMetrics:                              #Clase encargada de recolectar, calcular y auditar la telemetría de rendimiento de los algoritmos de búsqueda formal (BFS, UCS, A*) dentro del planificador
    def __init__(self):
        self.nodes_expanded = 0            # Número total de combinaciones de habilidades exploradas en el grafo   
        self.start_time = 0.0              #Tiempo inicial de la ejecucion
        self.execution_time_ms = 0.0       #Tiempo total consumido por el algoritmo
        self.path_length = 0               #Cantidad total de cursos que componen la ruta final

    def start_timer(self):               #inicia el cronometro calculando el tiempo total del sistema
        self.start_time = time.time()

    def stop_timer(self):                #Detiene el cronometro, calcula el tiempo trascurrido desde la ejecucion
        self.execution_time_ms = (time.time() - self.start_time) * 1000

    def to_dict(self):                   #Exporta los resultados de rendimiento recopilados en un formato de diccionario
        return {
            "nodes_expanded": self.nodes_expanded,
            "execution_time_ms": round(self.execution_time_ms, 2),
            "path_length": self.path_length
        }