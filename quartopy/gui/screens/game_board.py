from asyncio.log import logger
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QMessageBox, QPushButton, QGraphicsPixmapItem,
    QGraphicsItem, QGraphicsSimpleTextItem, QGraphicsTextItem
)
from PyQt5.QtGui import QPen, QColor, QPixmap, QPainter, QFont
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer
import sys 
import math

from quartopy.game.board import Board
from quartopy.game.piece import Piece, Size, Coloration, Shape, Hole
from quartopy.bot.human import  Quarto_bot
from quartopy.bot.random_bot import  Quarto_bot
from quartopy.game.quarto_game import QuartoGame

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
        self.current_container = None

    def mousePressEvent(self, event):
        # Solo permitir mover si es el turno del humano en la fase correcta
        if self.parent_board.human_action_phase == "IDLE":
            event.ignore()
            return
            
        # Solo permitir mover si la pieza está en el contenedor correcto según la fase
        if self.parent_board.human_action_phase == "PICK_TO_C4":
            # En esta fase, solo se pueden mover piezas que NO estén en el tablero
            if self.is_on_board:
                event.ignore()
                return
        elif self.parent_board.human_action_phase == "PLACE_FROM_C3":
            # En esta fase, solo se puede mover la pieza específica de container3
            if not (self.piece == self.parent_board.selected_piece_for_c3 and 
                    self.parentItem() == self.parent_board.container3):
                event.ignore()
                return
        
        # Solo guardar el estado original si no está ya en container3/4 ni en el tablero
        if not self.is_in_container_3_or_4 and not self.is_on_board:
            self.original_container = self.parentItem()
            self.original_position = self.pos()
        elif self.is_in_container_3_or_4:
            # Si está en container3/4, guardar ese como contenedor actual
            self.current_container = self.parentItem()
        
        self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        
        # Si no es el turno del humano, ignorar
        if self.parent_board.human_action_phase == "IDLE":
            self.return_to_original()
            super().mouseReleaseEvent(event)
            return
            
        current_scene_pos = self.scenePos()
        container3_rect = self.parent_board.container3.sceneBoundingRect()
        in_container3 = container3_rect.contains(current_scene_pos)
        container4_rect = self.parent_board.container4.sceneBoundingRect()
        in_container4 = container4_rect.contains(current_scene_pos)
        closest_cell = self.parent_board.find_closest_cell(current_scene_pos)
        
        game = self.parent_board.quarto_game

        if self.parent_board.human_action_phase == "PICK_TO_C4":
            if in_container4: # Human is picking a piece for the bot to place
                # Verificar que la pieza no esté ya en el tablero
                if self.is_on_board:
                    self.return_to_original()
                    super().mouseReleaseEvent(event)
                    return
                    
                self.is_on_board = False
                self.board_position = None
                
                # Limpiar container4 si ya hay una pieza
                if game.selected_piece: 
                    for item in self.parent_board.piece_items:
                        if item.piece == game.selected_piece and item.parentItem() == self.parent_board.container4:
                            item.return_to_original()
                            item.is_in_container_3_or_4 = False
                            break
                
                # Colocar la nueva pieza en container4
                game.selected_piece = self.piece
                self.place_in_container(self.parent_board.container4)
                self.is_in_container_3_or_4 = True
                self.is_on_board = False
                self.current_container = self.parent_board.container4
                
                # Cambiar fase y activar el turno del bot
                self.parent_board.human_action_phase = "IDLE"
                self.parent_board.current_turn = "BOT"
                self.parent_board.update_turn_display()  # Actualizar display
                game.cambiar_turno()
                QTimer.singleShot(500, self.parent_board.handle_bot_turn)
            else:
                self.return_to_original()
        
        elif self.parent_board.human_action_phase == "PLACE_FROM_C3":
            if closest_cell is not None and self.piece == self.parent_board.selected_piece_for_c3:
                row, col, cell = closest_cell
                if self.parent_board.try_place_piece_on_board(self, row, col):
                    self.is_on_board = True
                    self.is_in_container_3_or_4 = False
                    self.board_position = (row, col)
                    
                    # Limpiar container3
                    for p_item in self.parent_board.piece_items:
                        if p_item.piece == self.piece and p_item.parentItem() == self.parent_board.container3:
                            p_item.return_to_original()
                            p_item.is_in_container_3_or_4 = False
                            break
                    
                    # Verificar si el juego terminó
                    if self.parent_board.logic_board.check_win():
                        self.parent_board.human_action_phase = "IDLE"
                        self.parent_board.current_turn = "GAME_OVER"
                        self.parent_board.update_turn_display()  # Actualizar display
                        QMessageBox.information(self.parent_board, "¡Victoria!", "🎉 ¡Has ganado el juego!")
                        return
                    
                    # Preparar para siguiente ronda
                    self.parent_board.selected_piece_for_c3 = None
                    game.selected_piece = None
                    
                    # Verificar si el juego terminó (empate)
                    if self.parent_board.logic_board.is_full():
                        self.parent_board.human_action_phase = "IDLE"
                        self.parent_board.current_turn = "GAME_OVER"
                        self.parent_board.update_turn_display()  # Actualizar display
                        QMessageBox.information(self.parent_board, "¡Empate!", "El tablero está lleno, ¡es un empate!")
                        return
                    
                    # Cambiar a fase inicial para siguiente ronda
                    self.parent_board.human_action_phase = "PICK_TO_C4"
                    self.parent_board.current_turn = "HUMAN"
                    self.parent_board.update_turn_display()  # Actualizar display
                    game.cambiar_turno()
                else:
                    self.return_to_original()
            else:
                self.return_to_original()
        
        else:
            self.return_to_original()
        
        super().mouseReleaseEvent(event)
    
    def return_to_original(self):
        """Regresa la pieza a su posición original"""
        if self.is_on_board and self.board_position:
            # Si estaba en el tablero, mantenerla ahí
            row, col = self.board_position
            cell = self.parent_board.cells[row][col]
            self.setParentItem(cell)
            self.snap_to_cell(cell)
        elif self.is_in_container_3_or_4 and self.current_container:
            # Si estaba en container 3 o 4, mantenerla ahí
            self.setParentItem(self.current_container)
            self.place_in_container(self.current_container)
        elif self.original_container:
            # Regresar al contenedor original
            self.setParentItem(self.original_container)
            self.setPos(self.original_position)
            self.is_on_board = False
            self.is_in_container_3_or_4 = False
            self.current_container = self.original_container
    
    def remove_from_board(self):
        """Remueve la pieza del tablero lógico si estaba colocada"""
        if self.is_on_board and self.board_position:
            row, col = self.board_position
            self.parent_board.remove_piece_from_board(row, col)
            self.board_position = None
            self.is_on_board = False
    
    def place_in_container(self, container):
        """Coloca la pieza centrada en el contenedor especificado"""
        # Calcular posición centrada
        container_rect = container.boundingRect()
        piece_rect = self.boundingRect()
        
        center_x = (container_rect.width() - piece_rect.width()) / 2
        center_y = (container_rect.height() - piece_rect.height()) / 2 
        
        self.setParentItem(container)
        self.setPos(center_x, center_y)
        self.current_container = container

    def snap_to_cell(self, cell):
        """Ajusta la pieza a la celda especificada (centrada)"""
        cell_rect = cell.boundingRect()
        piece_rect = self.boundingRect()
        
        center_x = (cell_rect.width() - piece_rect.width()) / 2
        center_y = (cell_rect.height() - piece_rect.height()) / 2
        
        self.setParentItem(cell)
        self.setPos(center_x, center_y)
        self.current_container = None


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
        self.setPen(QPen(QColor("#FFD700"), 2))
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

        # --- Display de turno ---
        self.create_turn_display()

        # --- Lógica del tablero ---
        # Creación de los jugadores
        self.human_player =  Quarto_bot()
        self.bot_player =  Quarto_bot()
        self.quarto_game = QuartoGame(player1=self.human_player, player2=self.bot_player)
        self.logic_board = self.quarto_game.game_board

        # Estados del juego
        self.human_action_phase = "PICK_TO_C4"  # Fase inicial
        self.selected_piece_for_c3 = None
        self.current_turn = "HUMAN"  # HUMAN, BOT, GAME_OVER

        # --- Crear TODAS las piezas ---
        self.create_all_pieces()
        
        # Ajustar vista de la escena para ver todo
        self.scene.setSceneRect(0, 0, 1000, 700)

        # Radio de atracción a las celdas
        self.snap_distance = 80

    # ================================================================
    def create_turn_display(self):
        """Crea el display que muestra de quién es el turno"""
        # Crear rectángulo de fondo
        self.turn_display_bg = QGraphicsRectItem(0, 0, 100, 60)
        self.turn_display_bg.setPen(QPen(QColor("#FFD700"), 2))
        self.turn_display_bg.setBrush(QColor(0, 0, 0, 200))
        self.turn_display_bg.setPos(405, 30)
        self.scene.addItem(self.turn_display_bg)
        
        # Crear texto
        self.turn_display_text = QGraphicsTextItem("  TURNO")
        self.turn_display_text.setDefaultTextColor(QColor("#FFD700"))
        font = QFont("Arial", 12, QFont.Bold)
        self.turn_display_text.setFont(font)
        self.turn_display_text.setPos(415, 35)
        self.scene.addItem(self.turn_display_text)
        
        # Crear texto para el jugador actual
        self.current_player_text = QGraphicsTextItem("Humano")
        self.current_player_text.setDefaultTextColor(QColor("#FFFFFF"))
        font = QFont("Arial", 14, QFont.Bold)
        self.current_player_text.setFont(font)
        self.current_player_text.setPos(415, 55)
        self.scene.addItem(self.current_player_text)

    def update_turn_display(self):
        """Actualiza el display del turno según el estado actual"""
        if self.current_turn == "HUMAN":
            self.current_player_text.setPlainText("Humano")
            self.current_player_text.setDefaultTextColor(QColor("#4CAF50"))  # Verde
            # Actualizar color de fondo según fase
            if self.human_action_phase == "PICK_TO_C4":
                self.turn_display_bg.setBrush(QColor(76, 175, 80, 150))  # Verde transparente
            elif self.human_action_phase == "PLACE_FROM_C3":
                self.turn_display_bg.setBrush(QColor(255, 193, 7, 150))  # Amarillo transparente
        elif self.current_turn == "BOT":
            self.current_player_text.setPlainText("    Bot")
            self.current_player_text.setDefaultTextColor(QColor("#F44336"))  # Rojo
            self.turn_display_bg.setBrush(QColor(244, 67, 54, 150))  # Rojo transparente
        elif self.current_turn == "GAME_OVER":
            self.current_player_text.setPlainText("Fin")
            self.current_player_text.setDefaultTextColor(QColor("#9E9E9E"))  # Gris
            self.turn_display_bg.setBrush(QColor(158, 158, 158, 150))  # Gris transparente
        
        # Forzar actualización de la escena
        self.scene.update()

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
        
        return True

    def remove_piece_from_board(self, row: int, col: int):
        """Remueve una pieza del tablero (lógico y visual)"""
        if 0 <= row < 4 and 0 <= col < 4:
            # Limpiar tablero lógico
            if not self.logic_board.is_empty(row, col):
                self.logic_board.board[row][col] = 0
            
            # Limpiar celda visual
            cell = self.cells[row][col]
            if cell.piece_item:
                cell.piece_item.board_position = None
                cell.piece_item.is_on_board = False
                cell.piece_item.current_container = None
                cell.piece_item = None
            cell.setBrush(QColor("#000000"))

    # ================================================================
    def get_available_pieces(self):
        """Obtiene todas las piezas disponibles (no en tablero ni en container3/4)"""
        available_pieces = []
        for p_item in self.piece_items:
            if not p_item.is_on_board and not p_item.is_in_container_3_or_4:
                available_pieces.append(p_item.piece)
        return available_pieces

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
            (Piece(Size.TALL, Coloration.BLACK, Shape.CIRCLE, Hole.WITHOUT), "Quartopy/quartopy/gui/assets/images/bc0.png", 0, 0, self.container1),
            (Piece(Size.TALL, Coloration.BLACK, Shape.CIRCLE, Hole.WITH), "Quartopy/quartopy/gui/assets/images/bc1.png", 60, 0, self.container1),
            (Piece(Size.LITTLE, Coloration.BLACK, Shape.CIRCLE, Hole.WITHOUT), "Quartopy/quartopy/gui/assets/images/bc2.png", 120, 0, self.container1),
            (Piece(Size.LITTLE, Coloration.BLACK, Shape.CIRCLE, Hole.WITH), "Quartopy/quartopy/gui/assets/images/bc3.png", 180, 0, self.container1),
            (Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITHOUT), "Quartopy/quartopy/gui/assets/images/bs0.png", 0, 60, self.container1),
            (Piece(Size.TALL, Coloration.BLACK, Shape.SQUARE, Hole.WITH), "Quartopy/quartopy/gui/assets/images/bs1.png", 60, 60, self.container1),
            (Piece(Size.LITTLE, Coloration.BLACK, Shape.SQUARE, Hole.WITHOUT), "Quartopy/quartopy/gui/assets/images/bs2.png", 120, 60, self.container1),
            (Piece(Size.LITTLE, Coloration.BLACK, Shape.SQUARE, Hole.WITH), "Quartopy/quartopy/gui/assets/images/bs3.png", 180, 60, self.container1),
            
            # Piezas blancas - Container 2
            (Piece(Size.TALL, Coloration.WHITE, Shape.CIRCLE, Hole.WITHOUT), "Quartopy/quartopy/gui/assets/images/gc0.png", 0, 0, self.container2),
            (Piece(Size.TALL, Coloration.WHITE, Shape.CIRCLE, Hole.WITH), "Quartopy/quartopy/gui/assets/images/gc1.png", 60, 0, self.container2),
            (Piece(Size.LITTLE, Coloration.WHITE, Shape.CIRCLE, Hole.WITHOUT), "Quartopy/quartopy/gui/assets/images/gc2.png", 120, 0, self.container2),
            (Piece(Size.LITTLE, Coloration.WHITE, Shape.CIRCLE, Hole.WITH), "Quartopy/quartopy/gui/assets/images/gc3.png", 180, 0, self.container2),
            (Piece(Size.TALL, Coloration.WHITE, Shape.SQUARE, Hole.WITHOUT), "Quartopy/quartopy/gui/assets/images/gs0.png", 0, 60, self.container2),
            (Piece(Size.TALL, Coloration.WHITE, Shape.SQUARE, Hole.WITH), "Quartopy/quartopy/gui/assets/images/gs1.png", 60, 60, self.container2),
            (Piece(Size.LITTLE, Coloration.WHITE, Shape.SQUARE, Hole.WITHOUT), "Quartopy/quartopy/gui/assets/images/gs2.png", 120, 60, self.container2),
            (Piece(Size.LITTLE, Coloration.WHITE, Shape.SQUARE, Hole.WITH), "Quartopy/quartopy/gui/assets/images/gs3.png", 180, 60, self.container2),
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
            piece_item.current_container = container
            
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
    def update_cell_visual(self, row, col):
        cell = self.cells[row][col]
        cell.setBrush(QColor("#9c9a17"))

    def reset_board(self):
        # Limpiar tablero lógico
        self.quarto_game = QuartoGame(player1=self.human_player, player2=self.bot_player)
        self.logic_board = self.quarto_game.game_board
        
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
                piece_item.current_container = piece_item.original_container
        
        # Reiniciar fases
        self.human_action_phase = "PICK_TO_C4"
        self.selected_piece_for_c3 = None
        self.current_turn = "HUMAN"
        self.update_turn_display()

    # ================================================================
    def handle_bot_turn(self):
        """Maneja el turno completo del bot"""
        print(f"[DEBUG] handle_bot_turn called - current_turn: {self.current_turn}")
        
        if self.current_turn != "BOT":
            print(f"[DEBUG] Not bot's turn, current_turn: {self.current_turn}")
            return
            
        self.update_turn_display()  # Actualizar display
        QTimer.singleShot(300, self._execute_bot_turn)
    
    def _execute_bot_turn(self):
        """Ejecuta la lógica del turno del bot"""
        print(f"[DEBUG] _execute_bot_turn - quarto_game.pick: {self.quarto_game.pick}")
        
        game = self.quarto_game
        current_player = game.get_current_player()
        
        print(f"[DEBUG] Current player type: {type(current_player)}")
        print(f"[DEBUG] Is Random_bot? {isinstance(current_player,  Quarto_bot)}")
        
        if not isinstance(current_player,  Quarto_bot):
            print("[DEBUG] Not bot's turn according to game logic")
            return
        
        # Siempre comenzamos con la colocación (porque el humano ya seleccionó una pieza)
        # El bot debe colocar la pieza que está en container4
        self._bot_place_piece()
    
    def _bot_place_piece(self):
        """El bot coloca una pieza en el tablero"""
        print("[DEBUG] _bot_place_piece")
        
        game = self.quarto_game
        
        # Encontrar la pieza en container4
        piece_to_place = None
        piece_item_to_place = None
        
        for p_item in self.piece_items:
            if (p_item.parentItem() == self.container4 and 
                p_item.is_in_container_3_or_4):
                piece_to_place = p_item.piece
                piece_item_to_place = p_item
                print(f"[DEBUG] Found piece in container4: {piece_to_place}")
                break
        
        if not piece_to_place or not piece_item_to_place:
            print("[DEBUG] No piece found in container4")
            return
        
        # Bot coloca la pieza en el tablero
        print(f"[DEBUG] Bot placing piece: {piece_to_place}")
        row, col = game.get_current_player().place_piece(game, piece_to_place)
        print(f"[DEBUG] Bot placed at: ({row}, {col})")
        
        if self.try_place_piece_on_board(piece_item_to_place, row, col):
            piece_item_to_place.is_on_board = True
            piece_item_to_place.is_in_container_3_or_4 = False
            piece_item_to_place.board_position = (row, col)
            piece_item_to_place.current_container = None
            
            # Verificar si hay victoria
            if self.logic_board.check_win():
                print("[DEBUG] Bot won!")
                self.current_turn = "GAME_OVER"
                self.update_turn_display()
                QMessageBox.information(self, "¡Victoria!", "🎉 ¡El bot ha ganado!")
                return
            
            # Verificar si quedan piezas disponibles
            available_pieces = self.get_available_pieces()
            print(f"[DEBUG] Available pieces for C3: {len(available_pieces)}")
            
            if not available_pieces:
                print("[DEBUG] No more pieces available!")
                QTimer.singleShot(300, lambda: self._end_game_no_more_pieces())
                return
            
            # Ahora el bot elige una pieza para container3
            print("[DEBUG] Bot selecting piece for container3")
            QTimer.singleShot(300, self._bot_select_for_c3)
        else:
            print("[DEBUG] Bot failed to place piece")
    
    def _end_game_no_more_pieces(self):
        """Maneja el fin del juego cuando no hay más piezas"""
        print("[DEBUG] Game ended - no more pieces")
        if self.logic_board.check_win():
            self.current_turn = "GAME_OVER"
            self.update_turn_display()
            QMessageBox.information(self, "¡Victoria!", "🎉 ¡El bot ha ganado!")
        else:
            self.current_turn = "GAME_OVER"
            self.update_turn_display()
            QMessageBox.information(self, "¡Fin del juego!", "No hay más piezas disponibles. ¡Es un empate!")
        
        self.human_action_phase = "IDLE"
    
    def _bot_select_for_c3(self):
        """El bot selecciona una pieza para container3"""
        print("[DEBUG] _bot_select_for_c3")
        
        game = self.quarto_game
        
        # Primero cambiar a fase de selección
        game.cambiar_turno()  # Cambia a fase de selección
        print(f"[DEBUG] After cambiar_turno, game.pick: {game.pick}")
        
        # Obtener piezas disponibles
        available_pieces = self.get_available_pieces()
        print(f"[DEBUG] Number of available pieces: {len(available_pieces)}")
        
        if not available_pieces:
            print("[DEBUG] No available pieces for C3 selection!")
            self._end_game_no_more_pieces()
            return
        
        # Forzar al bot a usar solo piezas disponibles
        # Crear una versión modificada temporal del juego con solo piezas disponibles
        original_available_pieces = game.available_pieces.copy() if hasattr(game, 'available_pieces') else []
        
        # Actualizar las piezas disponibles en el juego
        game.available_pieces = available_pieces
        
        # Bot elige una pieza para container3
        print(f"[DEBUG] Available pieces for bot selection: {[str(p) for p in available_pieces]}")
        
        try:
            selected_piece_for_c3_logic = game.get_current_player().select(game)
            print(f"[DEBUG] Bot selected for C3: {selected_piece_for_c3_logic}")
        except Exception as e:
            print(f"[DEBUG] Error selecting piece: {e}")
            # Si hay error, seleccionar manualmente la primera disponible
            selected_piece_for_c3_logic = available_pieces[0] if available_pieces else None
        
        # Restaurar las piezas disponibles originales si existían
        if original_available_pieces:
            game.available_pieces = original_available_pieces
        elif hasattr(game, 'available_pieces'):
            delattr(game, 'available_pieces')
        
        if not selected_piece_for_c3_logic:
            print("[DEBUG] Bot failed to select a piece")
            return
        
        # Encontrar el PieceItem correspondiente
        piece_item_for_c3 = None
        for p_item in self.piece_items:
            if (p_item.piece == selected_piece_for_c3_logic and 
                not p_item.is_on_board and 
                not p_item.is_in_container_3_or_4):
                piece_item_for_c3 = p_item
                break
        
        if piece_item_for_c3:
            # Colocar la pieza en container3
            piece_item_for_c3.place_in_container(self.container3)
            piece_item_for_c3.is_in_container_3_or_4 = True
            piece_item_for_c3.is_on_board = False
            piece_item_for_c3.current_container = self.container3
            
            self.selected_piece_for_c3 = selected_piece_for_c3_logic
            
            # Cambiar turno y permitir al humano jugar
            game.cambiar_turno()  # Cambia a fase de colocación para el humano
            print(f"[DEBUG] After second cambiar_turno, game.pick: {game.pick}")
            
            self.human_action_phase = "PLACE_FROM_C3"
            self.current_turn = "HUMAN"
            self.update_turn_display()
            
            # Actualizar la interfaz
            self.update()
            print(f"[DEBUG] Human phase set to: {self.human_action_phase}")
        else:
            print(f"[DEBUG] Could not find piece item for C3 selection: {selected_piece_for_c3_logic}")
            print(f"[DEBUG] Available PieceItems state:")
            for p_item in self.piece_items:
                print(f"  - {p_item.piece}: is_on_board={p_item.is_on_board}, is_in_container={p_item.is_in_container_3_or_4}, parent={p_item.parentItem()}")
            
            # Intentar con otra pieza disponible
            if available_pieces:
                # Buscar cualquier pieza disponible
                for piece in available_pieces:
                    for p_item in self.piece_items:
                        if p_item.piece == piece and not p_item.is_on_board and not p_item.is_in_container_3_or_4:
                            # Usar esta pieza
                            p_item.place_in_container(self.container3)
                            p_item.is_in_container_3_or_4 = True
                            p_item.is_on_board = False
                            p_item.current_container = self.container3
                            self.selected_piece_for_c3 = piece
                            game.cambiar_turno()
                            self.human_action_phase = "PLACE_FROM_C3"
                            self.current_turn = "HUMAN"
                            self.update_turn_display()
                            self.update()
                            print(f"[DEBUG] Used fallback piece: {piece}")
                            return

# ================================================================

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = GameBoard()
    window.setWindowTitle("Quarto - Juego Completo")
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec_())