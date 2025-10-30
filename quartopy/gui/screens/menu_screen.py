# quarto_py/gui/screens/menu_screen.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt  

class MenuScreen(QWidget):
    """
    Representa la pantalla principal del menú del juego.
    Contiene opciones para iniciar el juego, ver reglas, etc.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. Crea el Layout (diseño) principal para apilar elementos
        layout = QVBoxLayout()
        
        # 2. Crea los Widgets
        
        # Título del menú
        title_label = QLabel("Menú Principal - Quarto")
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Los 4 botones
        self.btn_play = QPushButton('1. Jugar (Humano vs. Bot)')
        self.btn_multiplayer = QPushButton('2. Multijugador Local')
        self.btn_rules = QPushButton('3. Reglas del Juego')
        self.btn_exit = QPushButton('4. Salir')
        
        # 3. Añade los Widgets al Layout
        layout.addWidget(title_label)
        layout.addWidget(self.btn_play)
        layout.addWidget(self.btn_multiplayer)
        layout.addWidget(self.btn_rules)
        layout.addWidget(self.btn_exit)
        
        # Opcional: Centrar los botones y dejar espacio
        layout.addStretch(1) 
        
        # 4. Aplica el Layout
        self.setLayout(layout)