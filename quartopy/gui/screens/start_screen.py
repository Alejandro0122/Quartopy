import os
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPixmap

class StartScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Quarto - Inicio')

        self.background_pixmap = QPixmap(os.path.join(os.path.dirname(__file__), '../assets/images/Background.jpg'))

        # Título
        self.title_label = QLabel("¡Bienvenido al Juego Quarto!", self)
        self.title_label.setStyleSheet("""
            font-size: 24pt;
            font-weight: bold;
            color: white;
            background-color: rgba(0, 0, 0, 100);
            padding: 10px;
            border-radius: 10px;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFixedSize(600, 80)

        self.btn_style = ("""
            QPushButton {
                background-color: rgba(0, 0, 0, 180);
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

        # Botones
        self.start_button = QPushButton('Comenzar a Jugar', self)
        self.start_button.setStyleSheet(self.btn_style)
        self.start_button.setFixedSize(300, 60)
        self.exit_button = QPushButton('Salir', self)
        self.exit_button.setStyleSheet(self.btn_style)
        self.exit_button.setFixedSize(300, 60)

        # Layout
        layout = QVBoxLayout(self)
        layout.addStretch(1)
        layout.addWidget(self.title_label, 0, Qt.AlignCenter)
        layout.addSpacing(30)
        layout.addWidget(self.start_button, 0, Qt.AlignCenter)
        layout.addWidget(self.exit_button, 0, Qt.AlignCenter)
        layout.addStretch(1)

        self.setLayout(layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        target_rect = QRect(0, 0, self.width(), self.height())
        
        # Escalar la imagen para que llene el widget manteniendo la relación de aspecto (cover)
        scaled_pixmap = self.background_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        # Centrar la imagen escalada
        x = int((self.width() - scaled_pixmap.width()) / 2)
        y = int((self.height() - scaled_pixmap.height()) / 2)
        
        painter.drawPixmap(x, y, scaled_pixmap)
        
        super().paintEvent(event)

