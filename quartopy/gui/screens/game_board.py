from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QMessageBox, QPushButton, QGraphicsPixmapItem
)
from PyQt5.QtGui import QPen, QColor, QPixmap, QPainter
from PyQt5.QtCore import Qt, QRectF, QPointF

from game.board import Board
from game.piece import Piece, Size, Coloration, Shape, Hole


# ================================================================
# 🔷 Clase PieceItem (pieza movible con imagen)
# ================================================================
class PieceItem(QGraphicsPixmapItem):
    def __init__(self, piece: Piece, image_path: str):
        super().__init__()
        self.piece = piece
        self.setPixmap(QPixmap(image_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPixmapItem.ItemSendsScenePositionChanges, True)
        self.setCursor(Qt.OpenHandCursor)

    def mousePressEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)


# ================================================================
# 🔶 Clase Celda (Item individual clicable)
# ================================================================
class CellItem(QGraphicsRectItem):
    def __init__(self, row, col, parent_board):
        super().__init__()
        self.row = row
        self.col = col
        self.parent_board = parent_board

        # Tamaño de celda
        self.setRect(QRectF(0, 0, 100, 100))
        self.setPen(QPen(QColor("#efb810"), 2))
        self.setBrush(QColor("#3D3030"))

        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        self.setBrush(QColor("#5a4040"))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QColor("#3D3030"))
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        self.parent_board.handle_cell_click(self.row, self.col)
        super().mousePressEvent(event)


# ================================================================
# 🔷 Clase Tablero de Juego (GameBoard)
# ================================================================
class GameBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quarto - Tablero de Juego")

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")

        title_label = QLabel("TABLERO DE JUEGO QUARTO")
        title_label.setStyleSheet("font-size: 26pt; font-weight: bold; color: green;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # --- Escena y vista ---
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing, True)
        self.view.setAlignment(Qt.AlignCenter)
        self.view.setStyleSheet("background-color: #222; border: none;")
        layout.addWidget(self.view)

        # --- Tablero ---
        self.cells = []
        self.create_board_grid()

        # --- Botón salir ---
        self.btn_exit = QPushButton('Salir', self)
        self.btn_exit.setStyleSheet("""
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
        self.btn_exit.resize(100, 60)
        self.btn_exit.raise_()
        self.btn_exit.move(850, 370)

        # --- Contenedores ---
        cell_size = 60
        container_width = 4 * cell_size
        container_height = 2 * cell_size

        self.container1 = self.create_container(0, 100, container_width, container_height)
        self.container2 = self.create_container(535, 100, container_width, container_height)

        # --- Lógica del tablero ---
        self.logic_board = Board(name="game", storage=False, rows=4, cols=4)

        # --- Etiqueta de estado ---
        self.status_label = QLabel("Selecciona una celda para colocar una pieza.")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14pt; color: white; margin-top: 10px;")
        layout.addWidget(self.status_label)

        # --- Crear piezas de ejemplo ---
        self.create_example_pieces()

    # ================================================================
    def create_container(self, x, y, w, h):
        """Crea un contenedor con cuadrícula dorada."""
        container = QGraphicsRectItem(0, 0, w, h)
        container.setPen(QPen(QColor("#FFD700"), 2))
        container.setBrush(QColor(60, 60, 60, 180))
        container.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        container.setPos(x, y)
        self.scene.addItem(container)
        container.setRotation(90)

        # Líneas de cuadrícula
        for i in range(5):
            line = self.scene.addLine(i * 60, 0, i * 60, h, QPen(QColor("#FFD700"), 1))
            line.setParentItem(container)
        for j in range(3):
            line = self.scene.addLine(0, j * 60, w, j * 60, QPen(QColor("#FFD700"), 1))
            line.setParentItem(container)
        return container

    # ================================================================
    def create_example_pieces(self):
        """Crea dos piezas movibles dentro de los contenedores."""
        piece1 = Piece(Size.LITTLE, Coloration.WHITE, Shape.CIRCLE, Hole.WITHOUT)
        piece2 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)
        piece3 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)
        piece4 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)
        piece5 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)
        piece6 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)
        piece7 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)
        piece8 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)
        piece9 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)
        piece10 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)
        piece11 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)
        piece12 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)
        piece13 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)
        piece14 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)
        piece15 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)
        piece16 = Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH)

        # Usa tus imágenes PNG (ajusta las rutas a tu carpeta "images/")
        piece1_item = PieceItem(piece1, "Quartopy/quartopy/gui/assets/images/pieza2.png")
        piece2_item = PieceItem(piece2, "Quartopy/quartopy/gui/assets/images/pieza1.png")
        piece3_item = PieceItem(piece3, "Quartopy/quartopy/gui/assets/images/doradacir.png")
        piece4_item = PieceItem(piece4, "Quartopy/quartopy/gui/assets/images/pieza3.png")
        piece5_item = PieceItem(piece5, "Quartopy/quartopy/gui/assets/images/pieza4.png")
        piece6_item = PieceItem(piece5, "Quartopy/quartopy/gui/assets/images/pieza5.png")
        piece7_item = PieceItem(piece5, "Quartopy/quartopy/gui/assets/images/c1.png")
        piece8_item = PieceItem(piece5, "Quartopy/quartopy/gui/assets/images/c2.png")
        piece9_item = PieceItem(piece5, "Quartopy/quartopy/gui/assets/images/c3.png")
        piece10_item = PieceItem(piece5, "Quartopy/quartopy/gui/assets/images/c4.png")
        piece11_item = PieceItem(piece5, "Quartopy/quartopy/gui/assets/images/c5.png")
        piece12_item = PieceItem(piece5, "Quartopy/quartopy/gui/assets/images/c6.png")
        piece13_item = PieceItem(piece5, "Quartopy/quartopy/gui/assets/images/c7.png")
        piece14_item = PieceItem(piece5, "Quartopy/quartopy/gui/assets/images/c8.png")
        piece15_item = PieceItem(piece5, "Quartopy/quartopy/gui/assets/images/c9.png")
        piece16_item = PieceItem(piece5, "Quartopy/quartopy/gui/assets/images/c10.png")

        # Posición inicial dentro de los contenedores
        piece1_item.setPos(0, 0)
        piece2_item.setPos(60, 0)
        piece3_item.setPos(120, 0)
        piece4_item.setPos(180, 0)
        piece5_item.setPos(0, 60)
        piece6_item.setPos(60, 60)
        piece15_item.setPos(120, 60)
        piece16_item.setPos(180, 60)
        
        piece7_item.setPos(0, 0)
        piece8_item.setPos(60, 0)
        piece9_item.setPos(120, 0)
        piece10_item.setPos(180, 0)
        piece11_item.setPos(0, 60)
        piece12_item.setPos(60, 60)
        piece13_item.setPos(120, 60)
        piece14_item.setPos(180, 60)

        # Añadir a la escena (dentro del contenedor 1)
        piece1_item.setParentItem(self.container1)
        piece2_item.setParentItem(self.container1)
        piece3_item.setParentItem(self.container1)
        piece4_item.setParentItem(self.container1)
        piece5_item.setParentItem(self.container1)
        piece6_item.setParentItem(self.container1)
        piece7_item.setParentItem(self.container2)
        piece8_item.setParentItem(self.container2)
        piece9_item.setParentItem(self.container2)
        piece10_item.setParentItem(self.container2)
        piece11_item.setParentItem(self.container2)
        piece12_item.setParentItem(self.container2)
        piece13_item.setParentItem(self.container2)
        piece14_item.setParentItem(self.container2)
        piece15_item.setParentItem(self.container1)
        piece16_item.setParentItem(self.container1)
        
        self.scene.addItem(piece1_item)
        self.scene.addItem(piece2_item)
        self.scene.addItem(piece3_item)
        self.scene.addItem(piece4_item)
        self.scene.addItem(piece5_item)
        self.scene.addItem(piece6_item)
        self.scene.addItem(piece7_item)
        self.scene.addItem(piece8_item)
        self.scene.addItem(piece9_item)
        self.scene.addItem(piece10_item)
        self.scene.addItem(piece11_item)
        self.scene.addItem(piece12_item)
        self.scene.addItem(piece13_item)
        self.scene.addItem(piece14_item)
        self.scene.addItem(piece15_item)
        self.scene.addItem(piece16_item)

    # ================================================================
    def create_board_grid(self):
        """Crea la cuadrícula principal del tablero 4x4."""
        cell_size = 100
        spacing = 5
        start_x = 0
        start_y = 0

        for row in range(4):
            row_cells = []
            for col in range(4):
                cell = CellItem(row, col, self)
                x = start_x + col * (cell_size + spacing)
                y = start_y + row * (cell_size + spacing)
                cell.setPos(x, y)
                self.scene.addItem(cell)
                row_cells.append(cell)
            self.cells.append(row_cells)

        total_width = 4 * cell_size + 3 * spacing
        total_height = 4 * cell_size + 3 * spacing
        self.scene.setSceneRect(0, 0, total_width, total_height)

    # ================================================================
    def handle_cell_click(self, row, col):
        print(f"Clic en celda ({row}, {col})")

        if not self.logic_board.is_empty(row, col):
            QMessageBox.warning(self, "Celda ocupada", "⚠️ Esta celda ya está ocupada.")
            return

        piece = Piece(Size.LITTLE, Coloration.WHITE, Shape.CIRCLE, Hole.WITHOUT)
        self.logic_board.put_piece(piece, row, col)
        self.update_cell_visual(row, col)

        if self.logic_board.check_win():
            QMessageBox.information(self, "¡Victoria!", "🎉 ¡Has ganado el juego!")
            self.status_label.setText("Fin del juego - ¡Ganaste!")
        else:
            self.status_label.setText(f"Pieza colocada en ({row}, {col})")

    def update_cell_visual(self, row, col):
        cell = self.cells[row][col]
        cell.setBrush(QColor("#88c999"))

    def reset_board(self):
        self.logic_board = Board(name="game", storage=False, rows=4, cols=4)
        for row in self.cells:
            for cell in row:
                cell.setBrush(QColor("#3D3030"))
        self.status_label.setText("Tablero reiniciado.")
