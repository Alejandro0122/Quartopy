# quartopy/gui/screens/start_screen.py

import os
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie

class StartScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Tamaño de la ventana
        self.setWindowTitle('Quarto - Inicio')
        self.setGeometry(100, 100, 800, 600)  # Ventana más grande para que se vea la imagen

        # Ruta del GIF de fondo
        background_image_path = os.path.join(
            os.path.dirname(__file__), '../assets/images/tablero.gif'
        )
        background_image_path = os.path.abspath(background_image_path)

        # Label para el fondo (permite GIF animado)
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.setScaledContents(True)  # Ajusta la imagen al tamaño del label
        self.bg_label.lower()  # Asegura que el label quede detrás de los botones

        movie = QMovie(background_image_path)
        self.bg_label.setMovie(movie)
        movie.start()

        # Título
        self.title_label = QLabel("¡Bienvenido al Juego Quarto!", self)
        self.title_label.setStyleSheet("""
            font-size: 24pt;
            font-weight: bold;
            color: white;
            background-color: rgba(0, 0, 0, 100);  /* Fondo semitransparente */
            padding: 10px;
            border-radius: 10px;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.resize(600, 60)
        self.title_label.move((self.width() - self.title_label.width()) // 2, 50)

        # Botón para comenzar
        self.start_button = QPushButton('Comenzar a Jugar', self)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 180);  /* Fondo oscuro semitransparente */
                color: white;
                border: 2px solid white;
                padding: 15px;
                font-size: 14pt;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 50, 200);
            }
        """)
        self.start_button.resize(300, 60)
        self.start_button.move((self.width() - self.start_button.width()) // 2, 400)

        # Ajuste dinámico del fondo si se cambia el tamaño de la ventana
        self.resizeEvent = self.on_resize

    def on_resize(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.title_label.move((self.width() - self.title_label.width()) // 2, 50)
        self.start_button.move((self.width() - self.start_button.width()) // 2, 400)
