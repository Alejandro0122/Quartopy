# quartopy/gui/screens/type_player.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QGroupBox, QGridLayout, QCheckBox # Se añadió QCheckBox aquí
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
import sys
import subprocess # Importar el módulo subprocess para ejecutar comandos externos
import os         # Importar el módulo os para manejar rutas de archivos

class TypePlayerScreen(QWidget):
    """Pantalla para seleccionar el tipo de jugadores"""
    
    # Señal para notificar la selección de jugadores
    players_selected = pyqtSignal(dict)
    # Nueva señal para cancelar
    back_to_menu = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Título
        title_label = QLabel("CONFIGURACIÓN DE JUGADORES")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #FFD700; padding: 20px;")
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel("Selecciona el tipo de jugador para cada posición:")
        desc_label.setFont(QFont("Arial", 12))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("padding: 10px; color: #CCCCCC;")
        layout.addWidget(desc_label)
        
        # Contenedor para la configuración de jugadores
        config_group = QGroupBox("Configuración de Jugadores")
        config_group.setFont(QFont("Arial", 14, QFont.Bold))
        config_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #FFD700;
                border-radius: 10px;
                margin-top: 20px;
                padding-top: 10px;
                color: #FFD700;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        config_layout = QGridLayout()
        config_layout.setSpacing(15)
        
        # Jugador 1
        self.player1_label = QLabel("Jugador 1:")
        self.player1_label.setFont(QFont("Arial", 12))
        self.player1_label.setStyleSheet("color: #FFFFFF;")
        
        self.player1_combo = QComboBox()
        self.player1_combo.setFont(QFont("Arial", 11))
        self.player1_combo.addItems(["Humano", "Bot Aleatorio"])
        self.player1_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                min-width: 200px;
            }
            QComboBox:hover {
                border: 1px solid #FFD700;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #FFD700;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: white;
                selection-background-color: #FFD700;
                selection-color: black;
            }
        """)
        
        # Nota para Jugador 1
        self.player1_note = QLabel("(Inicia la partida)")
        self.player1_note.setFont(QFont("Arial", 10))
        self.player1_note.setStyleSheet("color: #AAAAAA; font-style: italic;")
        
        # Jugador 2
        self.player2_label = QLabel("Jugador 2:")
        self.player2_label.setFont(QFont("Arial", 12))
        self.player2_label.setStyleSheet("color: #FFFFFF;")
        
        self.player2_combo = QComboBox()
        self.player2_combo.setFont(QFont("Arial", 11))
        self.player2_combo.addItems(["Humano", "Bot Aleatorio"])
        self.player2_combo.setStyleSheet(self.player1_combo.styleSheet())
        
        # Nota para Jugador 2
        self.player2_note = QLabel("")
        
        # Añadir widgets al layout
        config_layout.addWidget(self.player1_label, 0, 0)
        config_layout.addWidget(self.player1_combo, 0, 1)
        config_layout.addWidget(self.player1_note, 0, 2)
        
        config_layout.addWidget(self.player2_label, 1, 0)
        config_layout.addWidget(self.player2_combo, 1, 1)
        config_layout.addWidget(self.player2_note, 1, 2)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Checkbox para Modo 2x2
        self.mode_2x2_checkbox = QCheckBox("Modo 2x2")
        self.mode_2x2_checkbox.setFont(QFont("Arial", 10))
        self.mode_2x2_checkbox.setStyleSheet("color: #CCCCCC; padding: 15px;")
        self.mode_2x2_checkbox.setChecked(False) # Por defecto, no marcado
        layout.addWidget(self.mode_2x2_checkbox)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        # Botón Volver
        self.back_btn = QPushButton("Volver")
        self.back_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.back_btn.setFixedSize(150, 50)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: 2px solid #777777;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #666666;
                border: 2px solid #888888;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        self.back_btn.clicked.connect(self.cancel_selection)
        
        # Botón Iniciar Juego
        self.start_btn = QPushButton("Iniciar Juego")
        self.start_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.start_btn.setFixedSize(200, 50)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: black;
                border: 2px solid #FFC400;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #FFC400;
                border: 2px solid #FFB300;
            }
            QPushButton:pressed {
                background-color: #FFB300;
            }
        """)
        self.start_btn.clicked.connect(self.start_game)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.back_btn)
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Conectar señales para actualizar la interfaz
        self.player1_combo.currentTextChanged.connect(self.update_ui)
        self.player2_combo.currentTextChanged.connect(self.update_ui)
        
        # Configuración inicial
        self.update_ui()
    
    def update_ui(self):
        """Actualiza la interfaz según las selecciones"""
        player1_type = self.player1_combo.currentText()
        player2_type = self.player2_combo.currentText()
        
        # Actualizar notas informativas
        if player1_type == "Humano":
            self.player1_note.setText("(Inicia la partida - Humano)")
        else:
            self.player1_note.setText("(Inicia la partida - Bot)")
            
        if player2_type == "Humano":
            self.player2_note.setText("(Humano)")
        else:
            self.player2_note.setText("(Bot)")
        
        # Actualizar colores de los combobox según selección
        player1_style = self.player1_combo.styleSheet()
        player2_style = self.player2_combo.styleSheet()
        
        if player1_type == "Humano":
            player1_style = player1_style.replace("border: 1px solid #555;", "border: 2px solid #4CAF50;")
        else:
            player1_style = player1_style.replace("border: 1px solid #555;", "border: 2px solid #2196F3;")
            
        if player2_type == "Humano":
            player2_style = player2_style.replace("border: 1px solid #555;", "border: 2px solid #4CAF50;")
        else:
            player2_style = player2_style.replace("border: 1px solid #555;", "border: 2px solid #2196F3;")
            
        self.player1_combo.setStyleSheet(player1_style)
        self.player2_combo.setStyleSheet(player2_style)
    
    def get_player_config(self):
        """Obtiene la configuración de jugadores seleccionada"""
        player1_type = self.player1_combo.currentText()
        player2_type = self.player2_combo.currentText()
        
        # Convertir a formato para el juego
        config = {
            'player1': 'human' if player1_type == "Humano" else 'random_bot',
            'player2': 'human' if player2_type == "Humano" else 'random_bot',
            'player1_display': player1_type,
            'player2_display': player2_type
        }
        
        return config
    
    def start_game(self):
        """Inicia el juego con la configuración seleccionada"""
        config = self.get_player_config()
        
        # Emitir señal inmediatamente sin confirmación (ahora también se inicia el CLI directamente)              
        self.players_selected.emit(config)  

        # Construir la ruta al script quarto_CLI.py
        # Se asume que quarto_CLI.py está en el directorio raíz del proyecto
        # La ruta del proyecto se obtiene del path del archivo actual (type_player.py)
        # y retrocediendo 3 niveles (screens -> gui -> quartopy -> project_root)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        quarto_cli_path = os.path.join(project_root, 'quarto_CLI.py')

        # Preparar los argumentos para el comando CLI                                                            
        command = [                                                                                              
            sys.executable,  # Usa el mismo intérprete de Python                                                 
            quarto_cli_path,                                                                                     
            "--player1", config['player1'],                                                                      
            "--player2", config['player2'],                                                                      
            "--delay", "0.5",  # Puedes ajustar el delay si es necesario                                         
        ]  
        
        # Si el checkbox de "Modo 2x2" está marcado, añadir el argumento al comando
        if self.mode_2x2_checkbox.isChecked():
            command.append("--mode_2x2")

        try:                                                                                                     
            # Ejecutar el comando CLI en un subproceso.                                                          
            # Esto permite que el juego de la CLI se ejecute de forma independiente.                             
            # Se usa `Popen` sin `wait()` para no bloquear la interfaz gráfica.                                  
            # `creationflags` es útil en Windows para que el nuevo proceso tenga su propia ventana de consola.   
            if sys.platform == "win32":                                                                          
                subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE)                           
            else:                                                                                                
                subprocess.Popen(command)                                                                        
            print(f"Juego CLI iniciado con: {config['player1']} vs {config['player2']}{' (Modo 2x2)' if self.mode_2x2_checkbox.isChecked() else ''}")                         
            # Opcionalmente, puedes cerrar la ventana actual de la GUI o hacer una transición                    
            # self.parentWidget().close() # Cierra la ventana principal de la GUI si esto es deseado      
        except FileNotFoundError:                                                                                
            print(f"Error: El script '{quarto_cli_path}' no se encontró.")                                       
        except Exception as e:                                                                                   
            print(f"Error al iniciar el juego CLI: {e}")   
    
    def cancel_selection(self):
        """Cancela la selección y vuelve al menú principal"""
        # Emitir la señal de volver al menú (sin argumentos)
        self.back_to_menu.emit()
    
    def showEvent(self, event):
        """Se ejecuta cuando se muestra la pantalla"""
        super().showEvent(event)
        # Restablecer selecciones por defecto
        self.player1_combo.setCurrentIndex(0)  # Humano
        self.player2_combo.setCurrentIndex(1)  # Bot Aleatorio


# Función de ejemplo para integrar esta pantalla
def test_type_player_screen():
    """Función de prueba para la pantalla de selección de jugadores"""
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    def on_players_selected(config):
        if config:
            print(f"Configuración seleccionada:")
            print(f"  Jugador 1: {config['player1']} ({config['player1_display']})")
            print(f"  Jugador 2: {config['player2']} ({config['player2_display']})")
            
            # Aquí podrías iniciar el juego con esta configuración
            # Por ejemplo:
            # from quartopy import go_quarto
            # go_quarto(player1_file=config['player1'], player2_file=config['player2'])
        else:
            print("Configuración cancelada - volviendo al menú")
        
        app.quit()
    
    def on_back_to_menu():
        print("Volviendo al menú principal")
        app.quit()
    
    screen = TypePlayerScreen()
    screen.players_selected.connect(on_players_selected)
    screen.back_to_menu.connect(on_back_to_menu)
    screen.setWindowTitle("Quarto - Selección de Jugadores")
    screen.resize(600, 400)
    screen.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    test_type_player_screen()