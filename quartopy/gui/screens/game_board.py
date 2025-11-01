from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QMessageBox, QPushButton, QGraphicsPixmapItem,
    QGraphicsItem, QGraphicsSimpleTextItem
)
from PyQt5.QtGui import QPen, QColor, QPixmap, QPainter
from PyQt5.QtCore import Qt, QRectF, QPointF
import sys 

from game.board import Board
from game.piece import Piece, Size, Coloration, Shape, Hole


# ================================================================
# 🔷 Clase PieceItem (pieza movible con imagen)
# ================================================================
class PieceItem(QGraphicsPixmapItem):
    def __init__(self, piece: Piece, image_path: str, parent_board: QWidget): 
        super().__init__()
        self.piece = piece
        self.parent_board = parent_board 
        self.setPixmap(QPixmap(image_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPixmapItem.ItemSendsScenePositionChanges, True)
        self.setCursor(Qt.OpenHandCursor)
        
        # Estado de la pieza
        self.is_in_container_3_or_4 = False
        self.original_container = None
        self.original_position = QPointF(0, 0)

    def mousePressEvent(self, event):
        # Solo guardar el estado original si no está ya en container3/4
        if not self.is_in_container_3_or_4:
            self.original_container = self.parentItem()
            self.original_position = self.pos()
        
        self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        
        # Obtener la posición actual en la escena
        current_scene_pos = self.scenePos()
        
        # Verificar colisión con container3
        container3_rect = self.parent_board.container3.sceneBoundingRect()
        in_container3 = container3_rect.contains(current_scene_pos)
        
        # Verificar colisión con container4
        container4_rect = self.parent_board.container4.sceneBoundingRect()
        in_container4 = container4_rect.contains(current_scene_pos)
        
        if in_container3:
            self.place_in_container(self.parent_board.container3)
            self.is_in_container_3_or_4 = True
            
        elif in_container4:
            self.place_in_container(self.parent_board.container4)
            self.is_in_container_3_or_4 = True
            
        else:
            # Si no está en container3/4, regresar al original
            if self.original_container and not self.is_in_container_3_or_4:
                self.setParentItem(self.original_container)
                self.setPos(self.original_position)
            # Si ya estaba en container3/4 pero se soltó fuera, dejarla donde está
        
        super().mouseReleaseEvent(event)
    
    def place_in_container(self, container):
        """Coloca la pieza centrada en el contenedor especificado"""
        # Calcular posición centrada
        container_rect = container.boundingRect()
        piece_rect = self.boundingRect()
        
        center_x = (container_rect.width() - piece_rect.width()) / 2
        center_y = (container_rect.height() - piece_rect.height()) / 2
        
        self.setParentItem(container)
        self.setPos(center_x, center_y)


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
        self.setBrush(QColor("#000000"))

        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        self.setBrush(QColor("#FFD700"))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QColor("#000000"))
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

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")

        title_label = QLabel("QUARTO")
        title_label.setStyleSheet("background-color: white; font-size: 16pt; font-weight: bold; color: black;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # --- Escena y vista ---
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing, True)
        self.view.setAlignment(Qt.AlignCenter)
        self.view.setStyleSheet("background-color: #0F0A07 ; border: none;")
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
        self.btn_exit.move(800, 500)

        # --- Contenedores ---
        cell_size = 60
        container_width = 4 * cell_size
        container_height = 2 * cell_size

        # Crear contenedores principales (1 y 2)
        self.container1 = self.create_container(0, 250, container_width, container_height, rotate=False)
        self.container2 = self.create_container(675, 250, container_width, container_height, rotate=False)

        # Contenedores de destino (3 y 4)
        self.container3 = self.create_simple_container(90, 100, 70, 70)
        self.container4 = self.create_simple_container(765, 100, 70, 70)

        # --- Lógica del tablero ---
        self.logic_board = Board(name="game", storage=False, rows=4, cols=4)

        # --- Crear TODAS las piezas ---
        self.create_all_pieces()
        
        # Ajustar vista de la escena para ver todo
        self.scene.setSceneRect(0, 0, 1000, 700)

    # ================================================================
    def create_simple_container(self, x, y, w, h):
        """Crea un contenedor simple sin rotación"""
        container = QGraphicsRectItem(0, 0, w, h)
        container.setPen(QPen(QColor("#FFD700"), 3))
        container.setBrush(QColor(0, 0, 0, 180))
        container.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        container.setPos(x, y)
        self.scene.addItem(container)
        return container

    def create_container(self, x, y, w, h, rotate=True, label=""):
        """Crea un contenedor con opción de rotación"""
        container = QGraphicsRectItem(0, 0, w, h)
        container.setPen(QPen(QColor("#FFD700"), 2))
        container.setBrush(QColor(0, 0, 0, 180))
        container.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        container.setPos(x, y)
        self.scene.addItem(container)
        
        if rotate:
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
    def create_all_pieces(self):
        """Crea las 16 piezas completas del juego Quarto"""
        # Lista de todas las piezas con sus propiedades y posiciones iniciales
        pieces_data = [
            # Piezas negras - Container 1
            (Piece(Size.TALL, Coloration.BLACK, Shape.CIRCLE, Hole.WITHOUT), "./quartopy/gui/assets/images/bc0.png", 0, 0, self.container1),
            (Piece(Size.TALL, Coloration.BLACK, Shape.CIRCLE, Hole.WITH), "./quartopy/gui/assets/images/bc1.png", 60, 0, self.container1),
            (Piece(Size.LITTLE, Coloration.BLACK, Shape.CIRCLE, Hole.WITHOUT), "./quartopy/gui/assets/images/bc2.png", 120, 0, self.container1),
            (Piece(Size.LITTLE, Coloration.BLACK, Shape.CIRCLE, Hole.WITH), "./quartopy/gui/assets/images/bc3.png", 180, 0, self.container1),
            (Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITHOUT), "./quartopy/gui/assets/images/bs0.png", 0, 60, self.container1),
            (Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH), "./quartopy/gui/assets/images/bs1.png", 60, 60, self.container1),
            (Piece(Size.LITTLE, Coloration.BLACK, Shape.SQUARE, Hole.WITHOUT), "./quartopy/gui/assets/images/bs2.png", 120, 60, self.container1),
            (Piece(Size.LITTLE, Coloration.BLACK, Shape.SQUARE, Hole.WITH), "./quartopy/gui/assets/images/bs3.png", 180, 60, self.container1),
            
            # Piezas blancas - Container 2
            (Piece(Size.TALL, Coloration.WHITE, Shape.CIRCLE, Hole.WITHOUT), "./quartopy/gui/assets/images/gc0.png", 0, 0, self.container2),
            (Piece(Size.TALL, Coloration.WHITE, Shape.CIRCLE, Hole.WITH), "./quartopy/gui/assets/images/gc1.png", 60, 0, self.container2),
            (Piece(Size.LITTLE, Coloration.WHITE, Shape.CIRCLE, Hole.WITHOUT), "./quartopy/gui/assets/images/gc2.png", 120, 0, self.container2),
            (Piece(Size.LITTLE, Coloration.WHITE, Shape.CIRCLE, Hole.WITH), "./quartopy/gui/assets/images/gc3.png", 180, 0, self.container2),
            (Piece(Size.TALL, Coloration.WHITE, Shape.SQUARE, Hole.WITHOUT), "./quartopy/gui/assets/images/gs0.png", 0, 60, self.container2),
            (Piece(Size.TALL, Coloration.WHITE, Shape.SQUARE, Hole.WITH), "./quartopy/gui/assets/images/gs1.png", 60, 60, self.container2),
            (Piece(Size.LITTLE, Coloration.WHITE, Shape.SQUARE, Hole.WITHOUT), "./quartopy/gui/assets/images/gs2.png", 120, 60, self.container2),
            (Piece(Size.LITTLE, Coloration.WHITE, Shape.SQUARE, Hole.WITH), "./quartopy/gui/assets/images/gs3.png", 180, 60, self.container2),
        ]
        
        # Crear todas las piezas
        self.piece_items = []
        for piece, image_path, x, y, container in pieces_data:
            piece_item = PieceItem(piece, image_path, self)
            piece_item.setPos(x, y)
            piece_item.setParentItem(container)
            
            # Inicializar estado original
            piece_item.original_container = container
            piece_item.original_position = QPointF(x, y)
            
            self.scene.addItem(piece_item)
            self.piece_items.append(piece_item)

    # ================================================================
    def create_board_grid(self):
        """Crea la cuadrícula principal del tablero 4x4."""
        cell_size = 100
        spacing = 5
        start_x = 250  # Posición central para el tablero
        start_y = 100

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
            
    def update_cell_visual(self, row, col):
        cell = self.cells[row][col]
        cell.setBrush(QColor("#9c9a17"))

    def reset_board(self):
        self.logic_board = Board(name="game", storage=False, rows=4, cols=4)
        for row in self.cells:
            for cell in row:
                cell.setBrush(QColor("#4C4D4A"))


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = GameBoard()
    window.setWindowTitle("Quarto - Juego Completo")
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec_())