# quarto_py/gui/screens/game_board.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class GameBoard(QWidget):
    """
    Representa el tablero de juego principal. 
    Aquí es donde se dibujarán las piezas, el tablero y la información del juego.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle('Quarto - Tablero de Juego')
        
        # Layout principal para el tablero
        layout = QVBoxLayout()
        
        # Título de prueba
        title_label = QLabel("TABLERO DE JUEGO QUARTO")
        title_label.setStyleSheet("font-size: 30pt; font-weight: bold; color: green;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Una etiqueta temporal para el mensaje (A futuro, será tu QGridLayout para el tablero)
        placeholder_label = QLabel("Aquí irá la lógica de juego: Tablero, Piezas y Estado.")
        placeholder_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(placeholder_label)
        
        # Añadir un 'stretch' para empujar el contenido hacia arriba
        layout.addStretch(1)
        
        self.setLayout(layout)