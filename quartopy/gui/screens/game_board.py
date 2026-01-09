from asyncio.log import logger
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QMessageBox, QPushButton, QGraphicsPixmapItem,
    QGraphicsItem, QGraphicsSimpleTextItem, QGraphicsTextItem
)
from PyQt5.QtGui import QPen, QColor, QPixmap, QPainter, QFont
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer, pyqtSignal
import sys 
import math

from quartopy.game.board import Board
from quartopy.game.piece import Piece, Size, Coloration, Shape, Hole
from quartopy.bot.human import Quarto_bot as HumanBot
from quartopy.bot.random_bot import Quarto_bot as RandomBot
from quartopy.models.Bot import BotAI
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
        if self.parent_board.game_over:
            event.ignore()
            return

        # Solo permitir mover si es el turno del humano en la fase correcta
        if self.parent_board._get_current_player_type() != 'human':
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
        if self.parent_board._get_current_player_type() != 'human':
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
                self.place_in_container(self.parent_board.container4)
                self.is_in_container_3_or_4 = True
                self.is_on_board = False
                self.current_container = self.parent_board.container4
                
                # Actualizar el juego lógico
                game.select_and_remove_piece(self.piece)
                
                move_info = {
                    "player_name": game.get_current_player().name,
                    "player_pos": game.player_turn,
                    "action": "selected",
                    "piece": self.piece.__repr__(verbose=True),
                    "piece_index": self.piece.index(),
                    "attempt": 1,
                }
                game.move_history.append(move_info)

                game.cambiar_turno() # Cambia a fase de colocación para el siguiente jugador

                # Determinar quién juega ahora (el oponente)
                next_player_type = self.parent_board._get_current_player_type()
                
                if next_player_type == 'human':
                    self.parent_board.human_action_phase = "PLACE_FROM_C3"
                    self.parent_board.selected_piece_for_c3 = self.piece # Set for human
                    self.parent_board.current_turn = "HUMAN"
                    self.parent_board.update_turn_display()
                else: # next_player_type is 'random_bot'
                    self.parent_board.human_action_phase = "IDLE" # No hay acción humana directa
                    self.parent_board.current_turn = "BOT"
                    self.parent_board.update_turn_display()
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
                    
                    move_info = {
                        "player_name": game.get_current_player().name,
                        "player_pos": game.player_turn,
                        "action": "placed",
                        "position": (row, col),
                        "position_index": game.game_board.pos2index(row, col),
                        "attempt": 1,
                        "board_after": game.game_board.serialize(),
                    }
                    game.move_history.append(move_info)

                    # Limpiar container3
                    for p_item in self.parent_board.piece_items:
                        if p_item.piece == self.piece and p_item.parentItem() == self.parent_board.container3:
                            p_item.return_to_original()
                            p_item.is_in_container_3_or_4 = False
                            break
                    
                    # Verificar si el juego terminó
                    if self.parent_board.logic_board.check_win(self.parent_board.quarto_game.mode_2x2):
                        winner = self.parent_board.quarto_game.get_current_player()
                        self.parent_board.end_game(winner.name)
                        return
                    
                    # Preparar para siguiente ronda
                    self.parent_board.selected_piece_for_c3 = None
                    game.selected_piece = 0 # Or None, consistent with QuartoGame

                    # Verificar si el juego terminó (empate)
                    if self.parent_board.logic_board.is_full():
                        self.parent_board.end_game()
                        return
                    
                    # Cambiar el turno lógico del juego para la fase de selección del próximo jugador
                    game.cambiar_turno() # Ahora el siguiente jugador debe seleccionar una pieza
                    
                    # Determinar quién juega ahora
                    next_player_type = self.parent_board._get_current_player_type()
                    
                    if next_player_type == 'human':
                        self.parent_board.human_action_phase = "PICK_TO_C4"
                        self.parent_board.current_turn = "HUMAN"
                        self.parent_board.update_turn_display()
                    else: # next_player_type is 'random_bot'
                        self.parent_board.human_action_phase = "IDLE" # No hay acción humana directa
                        self.parent_board.current_turn = "BOT"
                        self.parent_board.update_turn_display()
                        QTimer.singleShot(500, self.parent_board.handle_bot_turn)
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
    back_to_menu_signal = pyqtSignal()
    def __init__(
        self, 
        parent=None, 
        player1_type: str = 'human', 
        player2_type: str = 'random_bot', 
        mode_2x2: bool = False
    ):
        super().__init__(parent)
        self.player1_type = player1_type
        self.player2_type = player2_type
        self.match_number = 1

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
        self.btn_exit.move(800, 530)

        # --- Botón volver al menú ---
        self.btn_back_to_menu = QPushButton('Volver al Menú', self)
        self.btn_back_to_menu.setStyleSheet("""
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
        self.btn_back_to_menu.clicked.connect(self.go_back_to_menu)
        self.btn_back_to_menu.resize(165, 60)
        self.btn_back_to_menu.raise_()
        self.btn_back_to_menu.move(750, 460)

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
        # Creación de los jugadores dinámicamente
        self.player1_instance: BotAI
        if self.player1_type == 'human':
            self.player1_instance = HumanBot()
        else: # 'random_bot'
            self.player1_instance = RandomBot()

        self.player2_instance: BotAI
        if self.player2_type == 'human':
            self.player2_instance = HumanBot()
        else: # 'random_bot'
            self.player2_instance = RandomBot()
            
        self.quarto_game = QuartoGame(
            player1=self.player1_instance, 
            player2=self.player2_instance, 
            mode_2x2=mode_2x2
        )
        self.logic_board = self.quarto_game.game_board

        # Estados del juego
        self.selected_piece_for_c3 = None
        self.human_action_phase = "IDLE" # Por defecto, en espera
        self.current_turn = "IDLE"  # IDLE, HUMAN, BOT, GAME_OVER
        self.game_over = False

        # Determinar el estado inicial del juego basado en el tipo de jugador 1
        if self.player1_type == 'human':
            self.human_action_phase = "PICK_TO_C4"
            self.current_turn = "HUMAN"
        else: # player1_type is 'random_bot'
            self.current_turn = "BOT"

        # --- Crear TODAS las piezas ---
        self.create_all_pieces()
        
        # Ajustar vista de la escena para ver todo
        self.scene.setSceneRect(0, 0, 1000, 700)

        # Radio de atracción a las celdas
        self.snap_distance = 80
        
        # Inicializar display de turno
        self.update_turn_display()

        # Si el jugador 1 es un bot, iniciar su turno automáticamente
        if self.current_turn == "BOT":
            QTimer.singleShot(500, self.handle_bot_turn)

    def end_game(self, winner_name=None):
        """Maneja el fin del juego, muestra el resultado y guarda la partida."""
        self.game_over = True
        self.current_turn = "GAME_OVER"
        self.update_turn_display()

        # Guardar la partida
        self.quarto_game.export_history_to_csv(match_number=self.match_number, winner=winner_name or "Tie")
        self.match_number += 1

        if winner_name:
            QMessageBox.information(self, "¡Quarto!", f"¡El jugador {winner_name} ha ganado!")
        elif self.logic_board.is_full():
            QMessageBox.information(self, "¡Empate!", "El tablero está lleno. ¡Es un empate!")
        else:
            QMessageBox.warning(self, "Error", "El juego ha terminado por un error inesperado.")

    def go_back_to_menu(self):
        self.reset_board()
        self.match_number = 1
        self.back_to_menu_signal.emit()

    def _get_current_player_type(self) -> str:
        """Retorna el tipo del jugador actual ('human' o 'random_bot')."""
        if self.quarto_game.turn: # Player 1
            return self.player1_type
        else: # Player 2
            return self.player2_type

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

        # Crear namertags para jugador 1
        self.player1_tag = QGraphicsSimpleTextItem("")
        self.player1_tag.setFont(font)
        self.player1_tag.setPos(80, 55)
        self.scene.addItem(self.player1_tag)

        # Crear namertags para jugador 2
        self.player2_tag = QGraphicsSimpleTextItem("")
        self.player2_tag.setFont(font)
        self.player2_tag.setPos(750, 55)
        self.scene.addItem(self.player2_tag)

    def update_turn_display(self):
        """Actualiza el display del turno según el estado actual"""
        current_player_logic = self.quarto_game.get_current_player()
        
        # Determinar el nombre a mostrar para el turno central
        if current_player_logic is self.quarto_game.player1:
            display_name = "Jugador 1"
        else:
            display_name = "Jugador 2"

        if self.current_turn == "HUMAN":
            self.current_player_text.setPlainText(f"  {display_name}")
            self.current_player_text.setDefaultTextColor(QColor("#4CAF50"))  # Verde
            # Actualizar color de fondo según fase
            if self.human_action_phase == "PICK_TO_C4":
                self.turn_display_bg.setBrush(QColor(76, 175, 80, 150))  # Verde transparente
            elif self.human_action_phase == "PLACE_FROM_C3":
                self.turn_display_bg.setBrush(QColor(255, 193, 7, 150))  # Amarillo transparente
        elif self.current_turn == "BOT":
            self.current_player_text.setPlainText(f"  {display_name}")
            self.current_player_text.setDefaultTextColor(QColor("#F44336"))  # Rojo
            self.turn_display_bg.setBrush(QColor(244, 67, 54, 150))  # Rojo transparente
        elif self.current_turn == "GAME_OVER":
            self.current_player_text.setPlainText("Fin")
            self.current_player_text.setDefaultTextColor(QColor("#9E9E9E"))  # Gris
            self.turn_display_bg.setBrush(QColor(158, 158, 158, 150))  # Gris transparente
        
        # Actualizar player tags (lógica simplificada)
        self.player1_tag.setText(f"  Jugador 1 \n({self.quarto_game.player1.name})")
        if self.player1_type == 'human':
            self.player1_tag.setBrush(QColor("#4CAF50"))
        else:
            self.player1_tag.setBrush(QColor("#F44336"))

        self.player2_tag.setText(f"  Jugador 2 \n({self.quarto_game.player2.name})")
        if self.player2_type == 'human':
            self.player2_tag.setBrush(QColor("#4CAF50"))
        else:
            self.player2_tag.setBrush(QColor("#F44336"))

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
        self.quarto_game = QuartoGame(
            player1=self.player1_instance, 
            player2=self.player2_instance,
            mode_2x2=self.quarto_game.mode_2x2 # Mantener el modo 2x2 original
        )
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
        self.game_over = False
        self.human_action_phase = "PICK_TO_C4"
        self.selected_piece_for_c3 = None
        self.current_turn = "HUMAN"
        self.update_turn_display()

    # ================================================================
    def handle_bot_turn(self):
        """Maneja el turno completo del bot"""
        if self.game_over:
            return
        print(f"[DEBUG] handle_bot_turn called - current_turn: {self.current_turn}")
        
        if self.current_turn != "BOT":
            print(f"[DEBUG] Not bot's turn, current_turn: {self.current_turn}")
            return
            
        self.update_turn_display()  # Actualizar display
        QTimer.singleShot(300, self._execute_bot_turn)
    
    def _execute_bot_turn(self):
        """Ejecuta la lógica del turno del bot, manejando ambas fases (selección y colocación)."""
        print(f"[DEBUG] _execute_bot_turn - quarto_game.pick: {self.quarto_game.pick}")
        
        game = self.quarto_game
        current_player = game.get_current_player()
        
        print(f"[DEBUG] Current player type: {type(current_player)}")
        
        # Determine if it's the current player's turn to pick or place
        if game.pick: # Bot needs to select a piece
            self._bot_select_piece_for_opponent()
        else: # Bot needs to place a piece
            self._bot_place_piece()
    
    def _bot_place_piece(self):
        """El bot coloca una pieza en el tablero"""
        print("[DEBUG] _bot_place_piece")
        
        game = self.quarto_game
        piece_to_place = game.selected_piece # La pieza ya está seleccionada en la lógica del juego
        
        # Encontrar el PieceItem correspondiente
        piece_item_to_place = None
        for p_item in self.piece_items:
            # La pieza a colocar es la que está en game.selected_piece y que no está en el tablero principal
            if (p_item.piece == piece_to_place and not p_item.is_on_board):
                piece_item_to_place = p_item
                break        
        if not piece_item_to_place:
            print(f"[ERROR] No PieceItem found for selected piece: {piece_to_place}")
            self.end_game() # Manejar este caso de error
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

            move_info = {
                "player_name": game.get_current_player().name,
                "player_pos": game.player_turn,
                "action": "placed",
                "position": (row, col),
                "position_index": game.game_board.pos2index(row, col),
                "attempt": 1,
                "board_after": game.game_board.serialize(),
            }
            game.move_history.append(move_info)
            
            # Limpiar container3 si la pieza estaba allí
            if piece_item_to_place.parentItem() == self.container3:
                piece_item_to_place.setParentItem(None) # Quitar de container3
            
            # Verificar si hay victoria
            if self.logic_board.check_win(self.quarto_game.mode_2x2):
                winner = game.get_current_player()
                print(f"[DEBUG] Bot {winner.name} won!")
                self.end_game(winner.name)
                return
            
            # Resetear la pieza seleccionada en la lógica del juego
            game.selected_piece = 0 # O None, depende de cómo lo maneje QuartoGame

            # Verificar si quedan piezas disponibles
            available_pieces = self.get_available_pieces()
            print(f"[DEBUG] Available pieces: {len(available_pieces)}")
            
            if not available_pieces and not self.logic_board.check_win():
                print("[DEBUG] No more pieces available!")
                self.end_game()
                return
            
            # Cambiar el turno lógico del juego para la fase de selección del próximo jugador
            game.cambiar_turno() # Ahora el siguiente jugador debe seleccionar una pieza
            
            # Determinar quién juega ahora
            next_player_type = self._get_current_player_type()
            
            if next_player_type == 'human':
                self.human_action_phase = "PICK_TO_C4"
                self.current_turn = "HUMAN"
                self.update_turn_display()
                self.update()
                print(f"[DEBUG] Next is human to pick: {self.human_action_phase}")
            else: # next_player_type is 'random_bot'
                self.human_action_phase = "IDLE" # No hay acción humana directa
                self.current_turn = "BOT"
                self.update_turn_display()
                QTimer.singleShot(500, self.handle_bot_turn)
                print(f"[DEBUG] Next is bot to pick: {self.current_turn}")
        else:
            print("[DEBUG] Bot failed to place piece")
            # Podríamos implementar reintentos o un manejo de error más robusto aquí
            self.end_game() # Fallback en caso de que el bot elija una posición inválida
    

    
    def _bot_select_piece_for_opponent(self):
        """El bot selecciona una pieza para el oponente y la coloca en container3"""
        print("[DEBUG] _bot_select_piece_for_opponent")
        
        game = self.quarto_game
        current_bot = game.get_current_player()
        
        # Bot selecciona una pieza
        selected_piece_logic = current_bot.select(game)
        
        # Actualizar el juego lógico
        if not game.select_and_remove_piece(selected_piece_logic):
            # Si la pieza seleccionada por el bot no se encuentra (error de lógica del bot), terminar el juego.
            print(f"[ERROR] Bot selected an invalid piece that is not in storage: {selected_piece_logic}")
            self.end_game()
            return

        move_info = {
            "player_name": current_bot.name,
            "player_pos": game.player_turn,
            "action": "selected",
            "piece": selected_piece_logic.__repr__(verbose=True),
            "piece_index": selected_piece_logic.index(),
            "attempt": 1,
        }
        game.move_history.append(move_info)
        
        game.cambiar_turno() # Cambia a fase de colocación para el siguiente jugador

        # Encontrar el PieceItem correspondiente para moverlo a container3
        piece_item_to_move = None
        for p_item in self.piece_items:
            if p_item.piece == selected_piece_logic and not p_item.is_on_board and not p_item.is_in_container_3_or_4:
                piece_item_to_move = p_item
                break
        
        if piece_item_to_move:
            # Mover la pieza visualmente a container3
            piece_item_to_move.place_in_container(self.container3)
            piece_item_to_in_container_3_or_4 = True
            piece_item_to_move.is_on_board = False
            piece_item_to_move.current_container = self.container3
            
            self.selected_piece_for_c3 = selected_piece_logic # Usado por el humano para saber qué pieza colocar
            
            # Determinar quién juega ahora (el oponente)
            next_player_type = self._get_current_player_type()
            
            if next_player_type == 'human':
                self.human_action_phase = "PLACE_FROM_C3"
                self.current_turn = "HUMAN"
                self.update_turn_display()
                self.update()
                print(f"[DEBUG] Next is human to place: {self.human_action_phase}")
            else: # next_player_type is 'random_bot'
                self.human_action_phase = "IDLE" # No hay acción humana directa
                self.current_turn = "BOT"
                self.update_turn_display()
                QTimer.singleShot(500, self.handle_bot_turn)
                print(f"[DEBUG] Next is bot to place: {self.current_turn}")
        else:
            print(f"[ERROR] Could not find PieceItem for selected piece: {selected_piece_logic}")
            # Esto no debería pasar si get_current_player().select() devuelve una pieza válida
            # que está en el storage_board y no en el game_board.
            self.end_game() # Considerar terminar o manejar el error de otra forma

# ================================================================

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = GameBoard()
    window.setWindowTitle("Quarto - Juego Completo")
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec_())


# ================================================================
# Enlazar quarto_cli con typle_player (para seleccion de bot o humano en default Y boton 2x2 en play) Marco

# Layaouts de nombre de jugadores en game_board.py  MARCO

# Configurar game_board para que juegue bot vs bot (Depende de Type_player)  JAIRO

# Enlazar cvs con record_screen  MARCO

# Boton regresar al menu en game_board.py (Limpie)  Jairo  X "a medias :v"

# Enlazar condiciones de victoria de board.py a game_board.py  Jairo

# Opcional : musica   Jairo

