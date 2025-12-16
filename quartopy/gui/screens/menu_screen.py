import os
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie

class MenuScreen(QWidget):
    """
    Representa la pantalla principal del menú del juego.
    Contiene opciones para iniciar el juego, ver reglas, etc.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Menú Principal - Quarto")
        self.setGeometry(180, 150, 1000, 525)

        # Ruta del fondo
        background_image_path = os.path.join(
            os.path.dirname(__file__), '../assets/images/Background.jpg'
        )
        background_image_path = os.path.abspath(background_image_path)

        # Label para el fondo 
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        #self.bg_label.setScaledContents(True)  # Ajusta la imagen al tamaño del label
        self.bg_label.lower()  # Asegura que el label quede detrás de los botones

        movie = QMovie(background_image_path)
        self.bg_label.setMovie(movie)
        movie.start()


        pocy= 350
        # Título
        self.title_label = QLabel("Menú Principal - Quarto", self)
        self.title_label.setStyleSheet("font-size: 20pt; font-weight: bold; color : #FFD700;")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.resize(500, 50)
        self.title_label.move(250, 80)


        btn_style = """
            QPushButton {
                background-color: rgba(0, 0, 0, 180);  /* Fondo transparente */
                color: white;
                border: 2px solid white;
                padding: 15px;
                font-size: 14pt;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30); /* Un ligero color blanco/gris al pasar el ratón */
            }
        """

        # Botón 1: Jugar
        self.btn_play = QPushButton('Jugar contra IA', self)
        self.btn_play.resize(300, 60)
        self.btn_play.move(pocy, 190)
        self.btn_play.setStyleSheet(btn_style)

        # Botón 2: Multijugador
        self.btn_record = QPushButton('Tabla de puntajes', self)
        self.btn_record.resize(300, 60)
        self.btn_record.move(pocy, 265)
        self.btn_record.setStyleSheet(btn_style)

        # Botón 3: Reglas
        self.btn_rules = QPushButton('Reglas del Juego', self)
        self.btn_rules.resize(300, 60)
        self.btn_rules.move(pocy, 340)
        self.btn_rules.setStyleSheet(btn_style)

        # Botón 4: Salir
        self.btn_exit = QPushButton('Salir', self)
        self.btn_exit.resize(300, 60)
        self.btn_exit.move(pocy, 415)
        self.btn_exit.setStyleSheet(btn_style)

