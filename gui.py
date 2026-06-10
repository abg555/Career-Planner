import json
import sys
import re  
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,  QScrollArea, QLabel, QLineEdit, QPushButton, QGridLayout, QFrame, QTextEdit)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve

try:
    from llm_interface import LLMInterface
    from planner import Planner
except ImportError:
    LLMInterface = None
    Planner = None

COLOR_FONDO_APP = "#F1F5F9"      
COLOR_PANEL_BLANCO = "#FFFFFF"
COLOR_TEXTO_TITULO = "#1E293B"
COLOR_TEXTO_CUERPO = "#475569"
COLOR_TEXTO_MUTED = "#64748B"
COLOR_ACCENTO_NARANJA = "#F97316"
COLOR_ACCENTO_LLM = "#7C2D12"
COLOR_RESALTADO = "#FFEDD5"  

class CursoCard(QFrame):
    def __init__(self, curso_data):
        super().__init__()
        self.curso = curso_data
        self.init_ui()
        
    def init_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_PANEL_BLANCO};
                border-radius: 16px;
            }}
        """)
        self.setFixedHeight(280)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)
        
        # Guardamos referencias a los labels para poder actualizar sus contenidos con HTML resaltado
        self.title_label = QLabel(self.curso.get("title", "Curso"))
        self.title_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {COLOR_TEXTO_TITULO}; background: transparent;")
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)
        
        self.desc_label = QLabel(self.curso.get("description", "Sin descripción"))
        self.desc_label.setFont(QFont("Segoe UI", 11))
        self.desc_label.setStyleSheet(f"color: {COLOR_TEXTO_CUERPO}; background: transparent;")
        self.desc_label.setWordWrap(True)
        self.desc_label.setFixedHeight(45)
        layout.addWidget(self.desc_label)
        
        # Prerequisitos
        req_label = QLabel("Prerequisitos:")
        req_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        req_label.setStyleSheet(f"color: {COLOR_TEXTO_TITULO}; background: transparent;")
        layout.addWidget(req_label)
        
        self.req_content = QLabel("")
        self.req_content.setFont(QFont("Segoe UI", 10))
        self.req_content.setStyleSheet(f"color: {COLOR_TEXTO_CUERPO}; background: transparent;")
        self.req_content.setWordWrap(True)
        layout.addWidget(self.req_content)
        
        # Habilidades obtenidas
        eff_label = QLabel("Habilidades Obtenidas:")
        eff_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        eff_label.setStyleSheet(f"color: {COLOR_TEXTO_TITULO}; background: transparent;")
        layout.addWidget(eff_label)
        
        self.eff_content = QLabel("")
        self.eff_content.setFont(QFont("Segoe UI", 10))
        self.eff_content.setStyleSheet(f"color: {COLOR_TEXTO_CUERPO}; background: transparent;")
        self.eff_content.setWordWrap(True)
        layout.addWidget(self.eff_content)
        
        layout.addStretch()
        
        # Footer
        footer_layout = QHBoxLayout()
        
        self.badge_label = QLabel("")
        self.badge_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.badge_label.setStyleSheet(f"color: {COLOR_ACCENTO_NARANJA}; background-color: #FFF7ED; padding: 4px 8px; border-radius: 6px;")
        
        self.metricas_label = QLabel("")
        self.metricas_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.metricas_label.setStyleSheet(f"color: {COLOR_TEXTO_TITULO}; background: transparent;")
        
        footer_layout.addWidget(self.badge_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.metricas_label)
        layout.addLayout(footer_layout)
        
        self.setLayout(layout)
        
        # Inicializar los textos planos/originales en las tarjetas
        self.actualizar_textos_resaltados("")

    def resaltar_palabra(self, texto_original, termino):
        #Función auxiliar para resaltar con fondo la palabra buscada sin subrayar
        if not termino:
            return texto_original
        try:
            pattern = re.compile(re.escape(termino), re.IGNORECASE)
            return pattern.sub(f'<span style="background-color: {COLOR_RESALTADO}; color: {COLOR_ACCENTO_LLM}; border-radius: 4px; padding: 0 2px;">\\g<0></span>', texto_original)
        except Exception:
            return texto_original

    def actualizar_textos_resaltados(self, termino):
        #Aplica el subrayado dinámico sobre los labels de la tarjeta"""
        # Título
        self.title_label.setText(self.resaltar_palabra(self.curso.get("title", "Curso"), termino))
        
        # Descripción
        self.desc_label.setText(self.resaltar_palabra(self.curso.get("description", "Sin descripción"), termino))
        
        # Prerrequisitos
        req_list = self.curso.get("prerequisites", [])
        req_text = ", ".join([str(r).replace("_", " ").capitalize() for r in req_list]) if req_list else "None"
        self.req_content.setText(self.resaltar_palabra(req_text, termino))
        
        # Efectos
        eff_list = self.curso.get("effects", [])
        eff_text = ", ".join([str(e).replace("_", " ").capitalize() for e in eff_list]) if eff_list else "None"
        self.eff_content.setText(self.resaltar_palabra(eff_text, termino))
        
        # Footer (Modalidad, dificultad y métricas)
        modalidad = self.curso.get('modality', 'online').upper()
        dificultad = self.curso.get('difficulty', 'media').upper()
        self.badge_label.setText(self.resaltar_palabra(f"{modalidad} • {dificultad}", termino))
        
        metricas_text = f"${self.curso.get('cost')} USD | {self.curso.get('duration_hours')}h"
        self.metricas_label.setText(self.resaltar_palabra(metricas_text, termino))


class ModernCareerPlannerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Planificador de Trayectoria Profesional")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(f"background-color: {COLOR_FONDO_APP};")
        
        self.dataset = self.cargar_dataset()
        self.trayectorias_actuales = []
        self.prompt_actual = ""
        self.cards_catalogo = [] 
        
        self.init_ui()
        
    def cargar_dataset(self):
        try:
            with open('dataset.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"courses": [], "available_skills": []}
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        scroll = QScrollArea()
        scroll.setStyleSheet("QScrollArea { border: none; background-color: " + COLOR_FONDO_APP + "; }")
        scroll.setWidgetResizable(True)
        
        scroll_content = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(35, 40, 35, 20)
        main_layout.setSpacing(20)
        
        titulo = QLabel("Planificador de Trayectoria Profesional")
        titulo.setFont(QFont("Segoe UI", 34, QFont.Bold))
        titulo.setStyleSheet(f"color: {COLOR_TEXTO_TITULO};")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        subtitulo = QLabel("Diseña tu futuro académico, optimiza tu camino profesional.")
        subtitulo.setFont(QFont("Segoe UI", 14))
        subtitulo.setStyleSheet(f"color: {COLOR_TEXTO_MUTED};")
        subtitulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitulo)
        
        main_layout.addSpacing(15)
        
        search_frame = QFrame()
        search_frame.setStyleSheet(f"QFrame {{ background-color: {COLOR_PANEL_BLANCO}; border-radius: 16px; }}")
        search_frame.setFixedHeight(64)
        
        shadow_search = QGraphicsDropShadowEffect()
        shadow_search.setBlurRadius(12)
        shadow_search.setXOffset(0)
        shadow_search.setYOffset(4)
        shadow_search.setColor(QColor(0, 0, 0, 35))
        search_frame.setGraphicsEffect(shadow_search)
        
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(20, 0, 10, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Escribe tus objetivos (ej: Quiero aprender desarrollo web, presupuesto $150, 60 horas)...")
        self.search_input.setFont(QFont("Segoe UI", 13))
        self.search_input.setStyleSheet(f"QLineEdit {{ background-color: transparent; border: none; color: {COLOR_TEXTO_CUERPO}; padding: 5px; }} QLineEdit::placeholder {{ color: {COLOR_TEXTO_MUTED}; }}")
        self.search_input.returnPressed.connect(self.ejecutar_busqueda)
        
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_buscar.setStyleSheet(f"QPushButton {{ background-color: {COLOR_ACCENTO_NARANJA}; color: white; border: none; border-radius: 12px; padding: 10px 20px; }} QPushButton:hover {{ background-color: #EA580C; }} QPushButton:disabled {{ background-color: #CBD5E1; color: #94A3B8; }}")
        self.btn_buscar.setFixedSize(120, 46)
        self.btn_buscar.clicked.connect(self.ejecutar_busqueda)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_buscar)
        search_frame.setLayout(search_layout)
        main_layout.addWidget(search_frame)
        
        main_layout.addSpacing(20)
        
        self.results_section = QFrame()
        self.results_section.setStyleSheet(f"QFrame {{ background-color: {COLOR_PANEL_BLANCO}; border-radius: 16px; }}")
        self.results_section.setVisible(False)
        
        shadow_results = QGraphicsDropShadowEffect()
        shadow_results.setBlurRadius(12)
        shadow_results.setXOffset(0)
        shadow_results.setYOffset(4)
        shadow_results.setColor(QColor(0, 0, 0, 35))
        self.results_section.setGraphicsEffect(shadow_results)
        
        self.results_layout = QVBoxLayout()
        self.results_layout.setContentsMargins(20, 15, 20, 15)
        self.results_layout.setSpacing(15)
        self.results_section.setLayout(self.results_layout)
        main_layout.addWidget(self.results_section)
        
        main_layout.addSpacing(20)
        
        catalogo_header_layout = QHBoxLayout()
        
        cat_label = QLabel("Catálogo de Cursos Disponibles")
        cat_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        cat_label.setStyleSheet(f"color: {COLOR_TEXTO_TITULO};")
        catalogo_header_layout.addWidget(cat_label)
        
        catalogo_header_layout.addStretch()
        
        filtro_container = QFrame()
        filtro_container.setStyleSheet(f"QFrame {{ background-color: {COLOR_PANEL_BLANCO}; border-radius: 10px; }}")
        filtro_container.setFixedSize(220, 44)
        
        shadow_filtro = QGraphicsDropShadowEffect()
        shadow_filtro.setBlurRadius(10)
        shadow_filtro.setXOffset(0)
        shadow_filtro.setYOffset(3)
        shadow_filtro.setColor(QColor(0, 0, 0, 30))
        filtro_container.setGraphicsEffect(shadow_filtro)
        
        filtro_layout_interno = QHBoxLayout()
        filtro_layout_interno.setContentsMargins(10, 0, 10, 0)
        
        self.catalogo_search_input = QLineEdit()
        self.catalogo_search_input.setPlaceholderText("Filtrar catálogo...")
        self.catalogo_search_input.setFont(QFont("Segoe UI", 10))
        self.catalogo_search_input.setStyleSheet("QLineEdit { background-color: transparent; border: none; color: " + COLOR_TEXTO_CUERPO + "; }")
        self.catalogo_search_input.textChanged.connect(self.filtrar_catalogo)
        
        filtro_layout_interno.addWidget(self.catalogo_search_input)
        filtro_container.setLayout(filtro_layout_interno)
        catalogo_header_layout.addWidget(filtro_container)
        
        main_layout.addLayout(catalogo_header_layout)
        main_layout.addSpacing(10)
        
    
        self.grid_frame = QFrame()
        self.grid_frame.setStyleSheet("QFrame { background-color: transparent; }")
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)
        self.grid_frame.setLayout(self.grid_layout)
        main_layout.addWidget(self.grid_frame)
        
    
        cursos = self.dataset.get("courses", [])
        self.cards_catalogo = []
        for curso in cursos:
            card = CursoCard(curso)
            self.cards_catalogo.append(card)
            
        
        self.reorganizar_grid_catalogo(self.cards_catalogo)
        
        main_layout.addStretch()
        
        scroll_content.setLayout(main_layout)
        scroll.setWidget(scroll_content)
        
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.addWidget(scroll)
        central_widget.setLayout(central_layout)
        
    def reorganizar_grid_catalogo(self, lista_tarjetas_visibles):

        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None) 
        
        for i, card in enumerate(lista_tarjetas_visibles):
            fila = i // 3
            columna = i % 3
            self.grid_layout.addWidget(card, fila, columna)
            card.setVisible(True)

    def filtrar_catalogo(self, texto):
        
        termino = texto.lower().strip()
        tarjetas_filtradas = []
        
        for card in self.cards_catalogo:
            curso = card.curso
            
            reqs = " ".join([str(r) for r in curso.get("prerequisites", [])])
            effs = " ".join([str(e) for e in curso.get("effects", [])])
            
            contenido_tarjeta = (
                f"{curso.get('title', '')} "
                f"{curso.get('description', '')} "
                f"{reqs} "
                f"{effs} "
                f"{curso.get('modality', '')} "
                f"{curso.get('difficulty', '')} "
                f"${curso.get('cost', '')} usd "
                f"{curso.get('duration_hours', '')}h"
            ).lower()
            
            if termino in contenido_tarjeta:
                
                card.actualizar_textos_resaltados(texto.strip())
                tarjetas_filtradas.append(card)
            else:
                card.setVisible(False)
                
       
        self.reorganizar_grid_catalogo(tarjetas_filtradas)
    
    def ejecutar_busqueda(self):
        
        text_input = self.search_input.text().strip()
        if not text_input:
            return
        
        self.btn_buscar.setText("...")
        self.btn_buscar.setEnabled(False)
        self.search_input.setEnabled(False)
        QApplication.processEvents() 
        
        self.prompt_actual = text_input
        
        if not Planner or not LLMInterface:
            self.btn_buscar.setText("Buscar")
            self.btn_buscar.setEnabled(True)
            self.search_input.setEnabled(True)
            return
        
        
        self._clear_results()
        
        try:
            skills_list = self.dataset.get('available_skills', [])
            modalities_list = list(set([c['modality'] for c in self.dataset.get('courses', [])]))
            difficulties_list = list(set([c['difficulty'] for c in self.dataset.get('courses', [])]))
            courses_dict = {c['id']: c for c in self.dataset.get('courses', [])}
            
            llm = LLMInterface()
            
            
            goal_skills = llm.get_goals_from_text(text_input, skills_list)
            start_skills = llm.get_start_skill(text_input, skills_list)
            money = llm.get_money(text_input)
            time_hours = llm.get_time(text_input)
            modalities = llm.get_modality(text_input, modalities_list)
            difficulties = llm.get_difficulty(text_input, difficulties_list)
            
            if money == -1: money = 9999
            if time_hours == -1: time_hours = 9999
            
            if not goal_skills or len(goal_skills) == 0:
                self._clear_results()
                return
            
            planner = Planner(start_skills, goal_skills, modalities, difficulties, money, time_hours)
            trajectories = []
            es_ruta_adaptativa = False
            
           
            plan_bfs,_ = planner.run_bfs_planner()
            if plan_bfs: trajectories.append({"algorithm": "BFS", "plan": plan_bfs})
            
            plan_ucs,_ = planner.run_ucs_planner()
            if plan_ucs: trajectories.append({"algorithm": "UCS", "plan": plan_ucs})
            
            plan_astar,_ = planner.run_astar_planner()
            if plan_astar: trajectories.append({"algorithm": "A* Óptimo", "plan": plan_astar})
            
           
            if not trajectories:
                
                result_adaptive = planner.run_adaptive_planner()
                
                if result_adaptive and isinstance(result_adaptive, tuple) and len(result_adaptive) == 2:
                    mode, best_plan = result_adaptive
                    if best_plan:
                        trajectories.append({"algorithm": "Búsqueda Adaptativa", "plan": best_plan})
                        es_ruta_adaptativa = True
                elif result_adaptive:
                  
                    trajectories.append({"algorithm": "Búsqueda Adaptativa", "plan": result_adaptive})
                    es_ruta_adaptativa = True
            
          
            seen_plans = {}
            unique_trajectories = []
            
            for traj in trajectories:
                
                plan_ids = []
                for op in traj['plan']:
                    if isinstance(op, dict):
                        plan_ids.append(op.get('id'))
                    else:
                        plan_ids.append(op) 
                
                plan_tuple = tuple(sorted(plan_ids))
                if not plan_tuple:
                    continue
                    
                if plan_tuple not in seen_plans:
                    seen_plans[plan_tuple] = [traj["algorithm"]]
                    total_cost = sum(courses_dict[cid].get('cost', 0) for cid in plan_ids if cid in courses_dict)
                    total_time = sum(courses_dict[cid].get('duration_hours', 0) for cid in plan_ids if cid in courses_dict)
                    
                    unique_trajectories.append({
                        "algorithms": [traj["algorithm"]],
                        "plan": [{"id": cid} for cid in plan_ids],
                        "total_cost": total_cost,
                        "total_time": total_time
                    })
                else:
                    seen_plans[plan_tuple].append(traj["algorithm"])
                    for unique_traj in unique_trajectories:
                        unique_tuple = tuple(sorted([o['id'] for o in unique_traj['plan']]))
                        if unique_tuple == plan_tuple:
                            unique_traj["algorithms"].append(traj["algorithm"])
                            break
            
          
            if unique_trajectories:
                self._display_results(unique_trajectories, courses_dict)
                
               
                separator = QFrame()
                separator.setStyleSheet("QFrame { border-top: 2px dashed #CBD5E1; margin-top: 15px; margin-bottom: 15px; }")
                self.results_layout.addWidget(separator)
                
                if es_ruta_adaptativa:
                    
                    llm_header = QLabel("Evaluación Adaptativa del Consejero LLM")
                    llm_header.setFont(QFont("Segoe UI", 15, QFont.Bold))
                    llm_header.setStyleSheet(f"color: {COLOR_ACCENTO_LLM};")
                    self.results_layout.addWidget(llm_header)
                    
                  
                    adaptive_plan_ids = [op['id'] for op in unique_trajectories[0]['plan']]
                    cursos_completos = [courses_dict[cid] for cid in adaptive_plan_ids if cid in courses_dict]
                    
                    adaptive_eval = llm.evaluate_adaptive_trajectory(text_input, cursos_completos, modalities_list, difficulties_list)
                    
                    
                    if adaptive_eval and adaptive_eval.get('restricciones_relajadas'):
                        lbl_rest_title = QLabel("Restricciones que debieron flexibilizarse:")
                        lbl_rest_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
                        lbl_rest_title.setStyleSheet(f"color: {COLOR_TEXTO_TITULO}; margin-top: 5px;")
                        self.results_layout.addWidget(lbl_rest_title)
                        
                        for rest in adaptive_eval.get('restricciones_relajadas', []):
                            txt_rest = (f"• <b>{rest.get('restriccion', 'Restricción')}:</b> "
                                        f"Solicitado: <span style='color: #EF4444;'>{rest.get('solicitado', '-')}</span> | "
                                        f"Ofrecido: <span style='color: #10B981;'>{rest.get('ofrecido', '-')}</span><br>"
                                        f"<i>Razón: {rest.get('razon', '-')}</i>")
                            lbl_rest = QLabel(txt_rest)
                            lbl_rest.setFont(QFont("Segoe UI", 11))
                            lbl_rest.setStyleSheet(f"color: {COLOR_TEXTO_CUERPO}; padding-left: 15px;")
                            lbl_rest.setWordWrap(True)
                            self.results_layout.addWidget(lbl_rest)
                    
            
                    lbl_just_title = QLabel("Análisis pedagógico y beneficios de la ruta:")
                    lbl_just_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
                    lbl_just_title.setStyleSheet(f"color: {COLOR_TEXTO_TITULO}; margin-top: 15px;")
                    self.results_layout.addWidget(lbl_just_title)
                    
                    lbl_just = QLabel(adaptive_eval.get('justificacion_general', 'Sin análisis disponible.'))
                    lbl_just.setFont(QFont("Segoe UI", 11))
                    lbl_just.setStyleSheet(f"color: {COLOR_TEXTO_CUERPO}; padding-left: 15px; font-style: italic;")
                    lbl_just.setWordWrap(True)
                    self.results_layout.addWidget(lbl_just)
                    
                else:
                  
                    llm_header = QLabel("Orientación y Análisis del Asesor Académico")
                    llm_header.setFont(QFont("Segoe UI", 15, QFont.Bold))
                    llm_header.setStyleSheet(f"color: {COLOR_ACCENTO_LLM}; margin-top: 5px; margin-bottom: 5px;")
                    self.results_layout.addWidget(llm_header)
                    
                    trajectories_payload = {}
                    for traj in unique_trajectories:
                        algo_key = "/".join(traj['algorithms'])
                        trajectories_payload[algo_key] = [courses_dict[op['id']] for op in traj['plan'] if op['id'] in courses_dict]
                    
                   
                    audit_result = llm.compare_and_evaluate_trajectories(text_input, trajectories_payload)
                    
                    if audit_result:
                        
                        lbl_analisis_title = QLabel("Análisis Curricular de las Trayectorias:")
                        lbl_analisis_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
                        lbl_analisis_title.setStyleSheet(f"color: {COLOR_TEXTO_TITULO}; margin-top: 10px; margin-bottom: 5px;")
                        self.results_layout.addWidget(lbl_analisis_title)
                        
                        texto_analisis = audit_result.get('analisis_detallado_alternativas', 'No hay análisis disponible.')
                        
                       
                        bloques_rutas = [r.strip() for r in texto_analisis.split("<br><br>") if r.strip()]
                        
                        for bloque in bloques_rutas:
                            lbl_parrafo = QLabel()
                            
                           
                            lbl_parrafo.setTextFormat(Qt.TextFormat.RichText) 
                            
                            lbl_parrafo.setText(bloque)
                            lbl_parrafo.setFont(QFont("Segoe UI", 11))
                            lbl_parrafo.setStyleSheet(f"color: {COLOR_TEXTO_CUERPO}; padding-left: 15px; margin-bottom: 14px; line-height: 140%;")
                            lbl_parrafo.setWordWrap(True)
                            self.results_layout.addWidget(lbl_parrafo)
                        
                       
                        sub_separator = QFrame()
                        sub_separator.setStyleSheet("QFrame { border-top: 1px solid #E2E8F0; margin-top: 5px; margin-bottom: 12px; }")
                        self.results_layout.addWidget(sub_separator)
                        
                        lbl_guia_title = QLabel("Guía de Decisión (Evaluación de Trade-offs):")
                        lbl_guia_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
                        lbl_guia_title.setStyleSheet(f"color: {COLOR_TEXTO_TITULO}; margin-bottom: 5px;")
                        self.results_layout.addWidget(lbl_guia_title)
                        
                        texto_guia = audit_result.get('guia_orientacion_usuario', 'No hay orientación disponible.')
                        lbl_guia = QLabel()
                        
                     
                        lbl_guia.setTextFormat(Qt.TextFormat.RichText)
                        
                        lbl_guia.setText(texto_guia) 
                        lbl_guia.setFont(QFont("Segoe UI", 11))
                        lbl_guia.setStyleSheet(f"color: {COLOR_TEXTO_CUERPO}; padding-left: 15px;")
                        lbl_guia.setWordWrap(True)
                        self.results_layout.addWidget(lbl_guia)
            else:
                self._clear_results()
        
        except Exception as e:
            print(f"Error crítico en ejecución de búsqueda o auditoría LLM: {e}")
            import traceback
            traceback.print_exc()
            self._clear_results()
        
        finally:
            self.btn_buscar.setText("Buscar")
            self.btn_buscar.setEnabled(True)
            self.search_input.setEnabled(True)
    
    def _clear_results(self):
        while self.results_layout.count():
            widget = self.results_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        self.results_section.setVisible(False)
    
    def _display_results(self, trajectories, courses_dict):
        self._clear_results()
        self.results_section.setVisible(True)
        
        title = QLabel("Resultados de Búsqueda")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR_TEXTO_TITULO};")
        self.results_layout.addWidget(title)
        
        for i, traj in enumerate(trajectories, 1):
            if i > 1:
                separator = QFrame()
                separator.setStyleSheet("QFrame { border-top: 1px solid #E2E8F0; }")
                separator.setFixedHeight(1)
                self.results_layout.addWidget(separator)
            
            header_layout = QHBoxLayout()
            algo_names = "/".join(traj['algorithms'])
            algo_label = QLabel(f"RUTA {i} - {algo_names}")
            algo_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
            algo_label.setStyleSheet(f"color: {COLOR_ACCENTO_NARANJA};")
            header_layout.addWidget(algo_label)
            
            header_layout.addStretch()
            
            cost_label = QLabel(f"Total: ${traj['total_cost']}     ")
            cost_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
            cost_label.setStyleSheet(f"color: {COLOR_TEXTO_CUERPO};")
            header_layout.addWidget(cost_label)
            
            time_label = QLabel(f"{traj['total_time']} horas")
            time_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
            time_label.setStyleSheet(f"color: {COLOR_TEXTO_CUERPO};")
            header_layout.addWidget(time_label)
            
            header_frame = QFrame()
            header_frame.setLayout(header_layout)
            self.results_layout.addWidget(header_frame)
            
            courses_frame = QFrame()
            courses_frame.setStyleSheet(f"QFrame {{ background-color: #F8FAFC; border-radius: 8px; }}")
            courses_layout = QVBoxLayout()
            courses_layout.setContentsMargins(15, 10, 15, 10)
            courses_layout.setSpacing(8)
            
            for step, operator in enumerate(traj['plan'], 1):
                course_id = operator['id']
                if course_id not in courses_dict:
                    continue
                
                course = courses_dict[course_id]
                course_row = QHBoxLayout()
                
                step_label = QLabel(f"{step}.")
                step_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
                step_label.setStyleSheet(f"color: {COLOR_TEXTO_MUTED};")
                step_label.setFixedWidth(30)
                course_row.addWidget(step_label)
                
                title_label = QLabel(course.get('title', 'Sin título'))
                title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
                title_label.setStyleSheet(f"color: {COLOR_TEXTO_TITULO};")
                title_label.setMinimumWidth(200)
                course_row.addWidget(title_label)
                
                modality_label = QLabel(course.get('modality', '-').capitalize())
                modality_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
                modality_label.setAlignment(Qt.AlignCenter)
                modality_label.setStyleSheet(f"background-color: {COLOR_ACCENTO_NARANJA}; color: white; padding: 4px 8px; border-radius: 6px;")
                modality_label.setFixedWidth(95)
                course_row.addWidget(modality_label)
                
                difficulty_label = QLabel(course.get('difficulty', '-').capitalize())
                difficulty_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
                difficulty_label.setAlignment(Qt.AlignCenter)
                diff_colors = {'baja': '#10B981', 'media': '#F59E0B', 'alta': '#EF4444'}
                diff_color = diff_colors.get(course.get('difficulty', '').lower(), '#64748B')
                difficulty_label.setStyleSheet(f"background-color: {diff_color}; color: white; padding: 4px 8px; border-radius: 6px;")
                difficulty_label.setFixedWidth(95)
                course_row.addWidget(difficulty_label)
                
                cost = course.get('cost', 0)
                cost_label = QLabel(f"${cost} USD")
                cost_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
                cost_label.setAlignment(Qt.AlignCenter)
                cost_label.setStyleSheet("background-color: #CCFBF1; color: #115E59; padding: 4px 8px; border-radius: 6px;")
                cost_label.setFixedWidth(85)
                course_row.addWidget(cost_label)
                
                duration = course.get('duration_hours', 0)
                duration_label = QLabel(f"{duration}h")
                duration_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
                duration_label.setAlignment(Qt.AlignCenter)
                duration_label.setStyleSheet("background-color: #DBEAFE; color: #1E40AF; padding: 4px 8px; border-radius: 6px;")
                duration_label.setFixedWidth(65)
                course_row.addWidget(duration_label)
                
                course_row.addStretch()
                
                course_widget = QFrame()
                course_widget.setLayout(course_row)
                courses_layout.addWidget(course_widget)

            courses_frame.setLayout(courses_layout)
            self.results_layout.addWidget(courses_frame)
    
    def auditar_con_llm(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernCareerPlannerGUI()
    window.show()
    sys.exit(app.exec_())