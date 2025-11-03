from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QMessageBox, QPushButton, QGraphicsPixmapItem,
    QGraphicsItem, QGraphicsSimpleTextItem
)
from PyQt5.QtGui import QPen, QColor, QPixmap, QPainter
from PyQt5.QtCore import Qt, QRectF, QPointF
import sys 
import math

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
        self.is_on_board = False
        self.board_position = None  # (row, col) si está en el tablero
        self.original_container = None
        self.original_position = QPointF(0, 0)

    def mousePressEvent(self, event):
        # Solo guardar el estado original si no está ya en container3/4 ni en el tablero
        if not self.is_in_container_3_or_4 and not self.is_on_board:
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
        
        # Verificar si está cerca del tablero
        closest_cell = self.parent_board.find_closest_cell(current_scene_pos)
        
        if in_container3:
            self.remove_from_board()
            self.place_in_container(self.parent_board.container3)
            self.is_in_container_3_or_4 = True
            self.is_on_board = False
            
        elif in_container4:
            self.remove_from_board()
            self.place_in_container(self.parent_board.container4)
            self.is_in_container_3_or_4 = True
            self.is_on_board = False
            
        elif closest_cell is not None:
            # Intentar colocar en el tablero
            row, col, cell = closest_cell
            if self.parent_board.try_place_piece_on_board(self, row, col):
                self.is_on_board = True
                self.is_in_container_3_or_4 = False
                self.board_position = (row, col)
            else:
                # Si no se pudo colocar, regresar al lugar original
                self.return_to_original()
        else:
            # Si no está en ningún lugar válido, regresar al original
            self.return_to_original()
        
        super().mouseReleaseEvent(event)
    
    def return_to_original(self):
        """Regresa la pieza a su posición original"""
        if self.is_on_board and self.board_position:
            # Si estaba en el tablero, mantenerla ahí
            row, col = self.board_position
            cell = self.parent_board.cells[row][col]
            self.snap_to_cell(cell)
        elif self.is_in_container_3_or_4:
            # Si estaba en container 3 o 4, mantenerla ahí
            pass
        elif self.original_container:
            # Regresar al contenedor original
            self.setParentItem(self.original_container)
            self.setPos(self.original_position)
            self.is_on_board = False
            self.is_in_container_3_or_4 = False
    
    def remove_from_board(self):
        """Remueve la pieza del tablero lógico si estaba colocada"""
        if self.is_on_board and self.board_position:
            row, col = self.board_position
            self.parent_board.remove_piece_from_board(row, col)
            self.board_position = None
    
    def place_in_container(self, container):
        """Coloca la pieza centrada en el contenedor especificado"""
        # Calcular posición centrada
        container_rect = container.boundingRect()
        piece_rect = self.boundingRect()
        
        center_x = (container_rect.width() - piece_rect.width()) / 2
        center_y = (container_rect.height() - piece_rect.height()) / 2
        
        self.setParentItem(container)
        self.setPos(center_x, center_y)

    def snap_to_cell(self, cell):
        """Ajusta la pieza a la celda especificada (centrada)"""
        cell_rect = cell.boundingRect()
        piece_rect = self.boundingRect()
        
        center_x = (cell_rect.width() - piece_rect.width()) / 2
        center_y = (cell_rect.height() - piece_rect.height()) / 2
        
        self.setParentItem(cell)
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
        self.piece_item = None  # Referencia a la pieza colocada

        # Tamaño de celda
        self.setRect(QRectF(0, 0, 100, 100))
        self.setPen(QPen(QColor("#efb810"), 2))
        self.setBrush(QColor("#000000"))

        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        if self.piece_item is None:  # Solo resaltar si está vacía
            self.setBrush(QColor("#FFD700"))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if self.piece_item is None:  # Solo restaurar si está vacía
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

        # Radio de atracción a las celdas
        self.snap_distance = 80

    # ================================================================
    def find_closest_cell(self, scene_pos: QPointF):
        """Encuentra la celda más cercana a la posición dada
        Returns: (row, col, cell) o None si está muy lejos"""
        min_distance = float('inf')
        closest_cell = None
        closest_row = None
        closest_col = None
        
        for row in range(4):
            for col in range(4):
                cell = self.cells[row][col]
                cell_center = cell.sceneBoundingRect().center()
                
                # Calcular distancia euclidiana
                dx = scene_pos.x() - cell_center.x()
                dy = scene_pos.y() - cell_center.y()
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_cell = cell
                    closest_row = row
                    closest_col = col
        
        # Solo retornar si está dentro del radio de atracción
        if min_distance <= self.snap_distance:
            return (closest_row, closest_col, closest_cell)
        return None

    def try_place_piece_on_board(self, piece_item: PieceItem, row: int, col: int) -> bool:
        """Intenta colocar una pieza en el tablero
        Returns: True si se colocó exitosamente, False si la celda está ocupada"""
        
        # Verificar si la celda está vacía
        if not self.logic_board.is_empty(row, col):
            return False
        
        cell = self.cells[row][col]
        
        # Si ya había una pieza en esta celda (no debería pasar), rechazar
        if cell.piece_item is not None:
            return False
        
        # Si esta pieza ya estaba en otra celda, limpiar la anterior
        if piece_item.is_on_board and piece_item.board_position:
            old_row, old_col = piece_item.board_position
            self.remove_piece_from_board(old_row, old_col)
        
        # Colocar la pieza en el tablero lógico
        self.logic_board.put_piece(piece_item.piece, row, col)
        
        # Colocar la pieza visualmente
        piece_item.snap_to_cell(cell)
        cell.piece_item = piece_item
        
        # Actualizar el color de la celda
        cell.setBrush(QColor("#9c9a17"))
        
        # Verificar victoria
        if self.logic_board.check_win():
            QMessageBox.information(self, "¡Victoria!", "🎉 ¡Has ganado el juego!")
        
        return True

    def remove_piece_from_board(self, row: int, col: int):
        """Remueve una pieza del tablero (lógico y visual)"""
        if 0 <= row < 4 and 0 <= col < 4:
            # Limpiar tablero lógico
            if not self.logic_board.is_empty(row, col):
                self.logic_board.board[row][col] = 0
            
            # Limpiar celda visual
            cell = self.cells[row][col]
            cell.piece_item = None
            cell.setBrush(QColor("#000000"))

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
        # Funcionalidad deshabilitada - ahora se maneja con drag & drop

    def update_cell_visual(self, row, col):
        cell = self.cells[row][col]
        cell.setBrush(QColor("#9c9a17"))

    def reset_board(self):
        # Limpiar tablero lógico
        self.logic_board = Board(name="game", storage=False, rows=4, cols=4)
        
        # Limpiar celdas visuales
        for row in self.cells:
            for cell in row:
                cell.setBrush(QColor("#000000"))
                cell.piece_item = None
        
        # Regresar todas las piezas a sus contenedores originales
        for piece_item in self.piece_items:
            if piece_item.original_container:
                piece_item.setParentItem(piece_item.original_container)
                piece_item.setPos(piece_item.original_position)
                piece_item.is_on_board = False
                piece_item.is_in_container_3_or_4 = False
                piece_item.board_position = None


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = GameBoard()
    window.setWindowTitle("Quarto - Juego Completo")
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec_())