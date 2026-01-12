import os
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPixmap

class MenuScreen(QWidget):
    """
    Representa la pantalla principal del menú del juego.
    Contiene opciones para iniciar el juego, ver reglas, etc.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Menú Principal")

        self.background_pixmap = QPixmap(os.path.join(os.path.dirname(__file__), '../assets/images/Background.jpg'))

        # Título
        self.title_label = QLabel("Menú Principal", self)
        self.title_label.setStyleSheet("font-size: 20pt; font-weight: bold; color : #FFD700;")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFixedHeight(50)

        btn_style = """
            QPushButton {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                border: 2px solid white;
                padding: 15px;
                font-size: 14pt;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
            }
        """

        # Botones
        self.btn_play = QPushButton('Jugar', self)
        self.btn_play.setStyleSheet(btn_style)
        self.btn_play.setFixedSize(300, 60)

        self.btn_record = QPushButton('Tabla de puntajes', self)
        self.btn_record.setStyleSheet(btn_style)
        self.btn_record.setFixedSize(300, 60)

        self.btn_rules = QPushButton('Reglas del Juego', self)
        self.btn_rules.setStyleSheet(btn_style)
        self.btn_rules.setFixedSize(300, 60)

        self.btn_exit = QPushButton('Salir', self)
        self.btn_exit.setStyleSheet(btn_style)
        self.btn_exit.setFixedSize(300, 60)

        # Layout
        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.title_label, 0, Qt.AlignCenter)
        layout.addSpacing(30)
        layout.addWidget(self.btn_play, 0, Qt.AlignCenter)
        layout.addWidget(self.btn_record, 0, Qt.AlignCenter)
        layout.addWidget(self.btn_rules, 0, Qt.AlignCenter)
        layout.addWidget(self.btn_exit, 0, Qt.AlignCenter)
        layout.addStretch(1)
        
        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Escalar la imagen para que llene el widget manteniendo la relación de aspecto (cover)
        scaled_pixmap = self.background_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        # Centrar la imagen escalada
        x = int((self.width() - scaled_pixmap.width()) / 2)
        y = int((self.height() - scaled_pixmap.height()) / 2)
        
        painter.drawPixmap(x, y, scaled_pixmap)
        
        super().paintEvent(event)

