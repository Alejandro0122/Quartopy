# quarto_py/gui/screens/menu_screen.py

from PyQt5.QtWidgets import QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt

class MenuScreen(QWidget):
    """
    Representa la pantalla principal del menú del juego.
    Contiene opciones para iniciar el juego, ver reglas, etc.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Menú Principal - Quarto")
        self.setGeometry(100, 100, 600, 400)

        # Título
        self.title_label = QLabel("Menú Principal - Quarto", self)
        self.title_label.setStyleSheet("font-size: 20pt; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.resize(500, 50)
        self.title_label.move(50, 30)

        # Botón 1: Jugar
        self.btn_play = QPushButton('1. Jugar (Humano vs. Bot)', self)
        self.btn_play.resize(300, 40)
        self.btn_play.move(150, 100)

        # Botón 2: Multijugador
        self.btn_multiplayer = QPushButton('2. Multijugador Local', self)
        self.btn_multiplayer.resize(300, 40)
        self.btn_multiplayer.move(150, 150)

        # Botón 3: Reglas
        self.btn_rules = QPushButton('3. Reglas del Juego', self)
        self.btn_rules.resize(300, 40)
        self.btn_rules.move(150, 200)

        # Botón 4: Salir
        self.btn_exit = QPushButton('4. Salir', self)
        self.btn_exit.resize(300, 40)
        self.btn_exit.move(150, 250)
