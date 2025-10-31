import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtGui import QMovie
from game.board import Board


class GameBoard(QWidget):
    """
    Representa el tablero de juego principal. 
    Aquí es donde se dibujarán las piezas, el tablero y la información del juego.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Ruta del fondo
        background_image_path = os.path.join(
            os.path.dirname(__file__), '../assets/images/tablero.jpg'
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

        self.setWindowTitle('Quarto - Tablero de Juego')
        
        # Layout principal para el tablero
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # --- Título ---
        title_label = QLabel("TABLERO DE JUEGO QUARTO")
        title_label.setStyleSheet("font-size: 26pt; font-weight: bold; color: green;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # --- Layout para la cuadrícula 4x4 ---
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        layout.addLayout(self.grid_layout)

        # --- Crear botones de las celdas ---
        self.buttons = []
        for row in range(4):
            row_buttons = []
            for col in range(4):
                button = QPushButton()
                button.setFixedSize(100, 100)
                button.setStyleSheet("background-color: #e8e8e8; border: 2px solid #555;")
                button.clicked.connect(lambda _, r=row, c=col: self.handle_cell_click(r, c))
                self.grid_layout.addWidget(button, row, col)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

        # --- Placeholder de imagen por defecto (si deseas mostrar piezas gráficas luego) ---
        self.default_piece_icon = None  # o ruta a imagen por defecto, ej: "assets/piece.png"

        # --- Label de estado ---
        self.status_label = QLabel("Selecciona una celda para colocar una pieza.")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14pt; color: #333; margin-top: 10px;")
        layout.addWidget(self.status_label)

        layout.addStretch(1)

    # ================================================================
    def handle_cell_click(self, row: int, col: int):
        """
        Maneja el evento de clic en una celda del tablero.
        Coloca una pieza si está vacía, muestra advertencia si está ocupada.
        """

        if not self.logic_board.is_empty(row, col):
            QMessageBox.warning(self, "Celda ocupada", "⚠️ Esta celda ya está ocupada.")
            return

        # En este ejemplo no tenemos aún piezas reales, así que usamos un marcador de posición
        fake_piece = 1  # O bien, podrías pasar un objeto Piece válido si ya tienes la lógica de piezas

        # Colocar pieza en la lógica
        self.logic_board.put_piece(fake_piece, row, col)

        # Colocar visualmente la pieza (ej. cambiar color o imagen)
        self.update_cell_visual(row, col)

        # Verificar si hay victoria
        if self.logic_board.check_win():
            QMessageBox.information(self, "¡Victoria!", "🎉 ¡Has ganado el juego!")
            self.status_label.setText("Fin del juego - ¡Ganaste!")
        else:
            self.status_label.setText(f"Pieza colocada en ({row}, {col})")

    # ================================================================
    def update_cell_visual(self, row, col):
        """Actualiza visualmente una celda del tablero (ej. pone color o imagen)."""
        button = self.buttons[row][col]

        # Si tienes imágenes, puedes usar algo como:
        # pixmap = QPixmap("assets/piece.png").scaled(80, 80, Qt.KeepAspectRatio)
        # button.setIcon(QIcon(pixmap))
        # button.setIconSize(pixmap.rect().size())

        # Por ahora, solo cambiamos el color para indicar que está ocupada
        button.setStyleSheet("background-color: #88c999; border: 2px solid #222;")

    # ================================================================
    def reset_board(self):
        """Reinicia el tablero gráfico y lógico."""
        self.logic_board = Board(name="game", storage=False, rows=4, cols=4)
        for row in range(4):
            for col in range(4):
                self.buttons[row][col].setStyleSheet("background-color: #e8e8e8; border: 2px solid #555;")
        self.status_label.setText("Tablero reiniciado.")