# quartopy/gui/screens/type_player.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QMessageBox,
    QPushButton, QComboBox, QGroupBox, QGridLayout, QCheckBox, QInputDialog, QLineEdit
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QSize
import sys, os
from .add_bot_screen import AddBotScreen


class TypePlayerScreen(QWidget):
    """Pantalla para seleccionar el tipo de jugadores"""
    
    # Señal para notificar la selección de jugadores
    players_selected = pyqtSignal(dict)
    # Nueva señal para cancelar
    back_to_menu = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.player1_name = "Jugador 1"
        self.player2_name = "Jugador 2"
        self._loaded_bots = {} # To store dynamically loaded bot configurations
        self.setup_ui()
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
        self.setWindowFlags(Qt.FramelessWindowHint)
        
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
        self.player1_name_edit = QLineEdit(self.player1_name)
        self.player1_name_edit.setFont(QFont("Arial", 12))
        self.player1_name_edit.setStyleSheet("""
    QLineEdit { 
        background-color: rgba(255, 255, 255, 0.1); 
        border: 1px solid rgba(255, 255, 255, 0.5); 
        color: white; 
        padding: 4px; 
        border-radius: 3px;
    }
    QLineEdit:focus {
        border: 1px solid white; /* Se ilumina al editar */
    }
""")
        self.player1_name_edit.setFixedWidth(120)
        self.player1_name_edit.setReadOnly(True)
        self.player1_name_edit.mousePressEvent = lambda event: self.player1_name_edit.setReadOnly(False) if event.button() == Qt.LeftButton else QLineEdit.mousePressEvent(self.player1_name_edit, event)
        self.player1_name_edit.returnPressed.connect(lambda: self.player1_name_edit.setReadOnly(True))
        self.player1_name_edit.editingFinished.connect(lambda: self.player1_name_edit.setReadOnly(True))

        player1_layout = QHBoxLayout()
        player1_layout.addWidget(self.player1_name_edit)
        self.player1_clear_btn = QPushButton()
        self.player1_clear_btn.setIcon(QIcon("quartopy/gui/assets/images/Edit_button.png")) 
        self.player1_clear_btn.setIconSize(QSize(24, 24))
        self.player1_clear_btn.setFixedSize(30, 30)
        self.player1_clear_btn.setStyleSheet("background-color: transparent; border: none;")
        self.player1_clear_btn.clicked.connect(lambda: (self.player1_name_edit.setReadOnly(False), self.player1_name_edit.clear(), self.player1_name_edit.setFocus()))
        player1_layout.addWidget(self.player1_clear_btn)

        
        self.player1_combo = QComboBox()
        self.player1_combo.setFont(QFont("Arial", 11))
        self.player1_combo.addItems(["Humano", "Bot Aleatorio", "Bot Minimax", "Bot CNN"])
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
        
        # Jugador 2
        self.player2_name_edit = QLineEdit(self.player2_name)
        self.player2_name_edit.setFont(QFont("Arial", 12))
        self.player2_name_edit.setStyleSheet("""
    QLineEdit { 
        background-color: rgba(255, 255, 255, 0.1); 
        border: 1px solid rgba(255, 255, 255, 0.5); 
        color: white; 
        padding: 4px; 
        border-radius: 3px;
    }
    QLineEdit:focus {
        border: 1px solid white; /* Se ilumina al editar */
    }
""")
        self.player2_name_edit.setFixedWidth(120)
        self.player2_name_edit.setReadOnly(True)
        self.player2_name_edit.mousePressEvent = lambda event: self.player2_name_edit.setReadOnly(False) if event.button() == Qt.LeftButton else QLineEdit.mousePressEvent(self.player2_name_edit, event)
        self.player2_name_edit.returnPressed.connect(lambda: self.player2_name_edit.setReadOnly(True))
        self.player2_name_edit.editingFinished.connect(lambda: self.player2_name_edit.setReadOnly(True))

        player2_layout = QHBoxLayout()
        player2_layout.addWidget(self.player2_name_edit)
        self.player2_clear_btn = QPushButton()
        self.player2_clear_btn.setIcon(QIcon("quartopy/gui/assets/images/Edit_button.png"))
        self.player2_clear_btn.setIconSize(QSize(24, 24))
        self.player2_clear_btn.setFixedSize(30, 30)
        self.player2_clear_btn.setStyleSheet("background-color: transparent; border: none;")
        self.player2_clear_btn.clicked.connect(lambda: (self.player2_name_edit.setReadOnly(False), self.player2_name_edit.clear(), self.player2_name_edit.setFocus()))
        player2_layout.addWidget(self.player2_clear_btn)
        
        self.player2_combo = QComboBox()
        self.player2_combo.setFont(QFont("Arial", 11))
        self.player2_combo.addItems(["Humano", "Bot Aleatorio", "Bot Minimax", "Bot CNN"])
        self.player2_combo.setStyleSheet(self.player1_combo.styleSheet())
        
        # Nota para Jugador 2
        self.player2_note = QLabel("")
        
        # Añadir widgets al layout
        config_layout.addLayout(player1_layout, 0, 0)
        config_layout.addWidget(self.player1_combo, 0, 1)

        config_layout.addLayout(player2_layout, 1, 0)
        config_layout.addWidget(self.player2_combo, 1, 1)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Checkbox para Modo 2x2
        self.mode_2x2_checkbox = QCheckBox("Modo 2 x 2")
        self.mode_2x2_checkbox.setFont(QFont("Arial", 14))
        layout.addWidget(self.mode_2x2_checkbox, alignment=Qt.AlignCenter)
        self.mode_2x2_checkbox.setChecked(False) 
        self.mode_2x2_checkbox.setStyleSheet("""
    QCheckBox {
        color: white;
    }
    QCheckBox::indicator {
        border: 2px solid #FFC400;
        background: #1a1a1a;
        width: 18px;
        height: 18px;
        border-radius: 3px;
    }
    QCheckBox::indicator:checked {
        background-color: #FFC400;
        border: 2px solid #FFC400;
        color: black;
    }
""")
        
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
        
        # Botón para agregar bot
        self.add_bot_btn = QPushButton("Agregar Bot")
        self.add_bot_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.add_bot_btn.setFixedSize(150, 50)
        self.add_bot_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: 2px solid #0056b3;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #0056b3;
                border: 2px solid #003F7F;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        self.add_bot_btn.clicked.connect(self._open_add_bot_screen)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_bot_btn) # Add new button here
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
        
        # Actualizar colores de los combobox según selección
        base_style = self.player1_combo.styleSheet()

        def get_style_for_type(p_type, style):
            if p_type == "Humano":
                return style.replace("border: 1px solid #555;", "border: 2px solid #4CAF50;")
            elif p_type == "Bot Minimax":
                return style.replace("border: 1px solid #555;", "border: 2px solid #F44336;") # Red for Minimax
            elif p_type == "Bot CNN":
                return style.replace("border: 1px solid #555;", "border: 2px solid #FF9800;")
            else: # Random Bot
                return style.replace("border: 1px solid #555;", "border: 2px solid #2196F3;")

        self.player1_combo.setStyleSheet(get_style_for_type(player1_type, base_style))
        self.player2_combo.setStyleSheet(get_style_for_type(player2_type, base_style))

    def get_player_config(self):
        """Obtiene la configuración de jugadores seleccionada"""
        
        def _get_player_details(combo_text):
            if combo_text == "Humano":
                return {'type': 'human', 'display_name': 'Humano'}
            elif combo_text in self._loaded_bots:
                bot_info = self._loaded_bots[combo_text]
                return {
                    'type': 'custom_bot',
                    'display_name': bot_info['bot_name'],
                    'bot_class': bot_info['bot_class'],        # CNNBot
                    'model_class': bot_info['model_class'],    # QuartoCNN
                    'weights_path': bot_info['weights_path']    # Ruta al .pt de los pesos
                }
            elif combo_text == "Bot Minimax":
                return {'type': 'minimax_bot', 'display_name': 'Bot Minimax'}
            elif combo_text == "Bot CNN":
                return {'type': 'cnn_bot', 'display_name': 'Bot CNN'}
            else: # "Bot Aleatorio"
                return {'type': 'random_bot', 'display_name': 'Bot Aleatorio'}

        player1_details = _get_player_details(self.player1_combo.currentText())
        player2_details = _get_player_details(self.player2_combo.currentText())

        config = {
            'player1_config': player1_details,
            'player2_config': player2_details,
            'player1_name': self.player1_name_edit.text(),
            'player2_name': self.player2_name_edit.text()
        }
        
        return config
    
    def start_game(self):
        """Inicia el juego con la configuración seleccionada"""
        config = self.get_player_config()
        config['mode_2x2'] = self.mode_2x2_checkbox.isChecked() # Add mode_2x2 to config
        
        self.players_selected.emit(config)   
    
    def cancel_selection(self):
        """Cancela la selección y vuelve al menú principal"""
        # Emitir la señal de volver al menú (sin argumentos)
        self.back_to_menu.emit()
    
    def _open_add_bot_screen(self):
        """Abre la mini pantalla para agregar un nuevo bot"""
        add_bot_dialog = AddBotScreen(self)
        add_bot_dialog.bot_added_successfully.connect(self._add_loaded_bot_to_combos)
        add_bot_dialog.exec_()
    
    def _add_loaded_bot_to_combos(self, bot_config: dict):
        """Añade un bot cargado dinámicamente a los QComboBoxes de selección."""
        bot_name = bot_config['bot_name']
        self._loaded_bots[bot_name] = bot_config
        self.player1_combo.addItem(bot_name)
        self.player2_combo.addItem(bot_name)

    def showEvent(self, event):
        """Se ejecuta cuando se muestra la pantalla"""
        super().showEvent(event)
        # Limpiar bots cargados y resetear QComboBoxes
        self._loaded_bots = {}
        self.player1_combo.clear()
        self.player2_combo.clear()
        self.player1_combo.addItems(["Humano", "Bot Aleatorio", "Bot Minimax", "Bot CNN"])
        self.player2_combo.addItems(["Humano", "Bot Aleatorio", "Bot Minimax", "Bot CNN"])

        # Restablecer selecciones por defecto
        self.player1_combo.setCurrentIndex(0)  # Humano
        self.player2_combo.setCurrentIndex(1)  # Bot Aleatorio
        self.player1_name_edit.setText("Jugador 1")
        self.player1_name_edit.setReadOnly(True)
        self.player2_name_edit.setText("Jugador 2")
        self.player2_name_edit.setReadOnly(True)


# Función de ejemplo para integrar esta pantalla
def test_type_player_screen():
    """Función de prueba para la pantalla de selección de jugadores"""
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    def on_players_selected(config):
        if config:
            print(f"Configuración seleccionada:")
            print(f"  Jugador 1 {config['player1']} ({config['player1_display']})")
            print(f"  Jugador 2 {config['player2']} ({config['player2_display']})")
            
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