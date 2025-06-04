from .board import Board
from ..models.Bot import BotAI
from .piece import Piece
from ..utils.logger import logger

from colorama import Fore, Back, Style
from os import path, makedirs
from datetime import datetime
import csv

logger.debug(f"{__name__} importado correctamente")


class QuartoGame:

    def __init__(self, player1: BotAI, player2: BotAI):
        self.MAX_TRIES = 16  # todos los intentos posibles
        self.TIE = "Tie"

        self.selected_piece: Piece | int = 0
        self.game_board = Board("Game Board", False, 4, 4)
        self.storage_board = Board("Storage Board", True, 2, 8)
        self.turn = True  # True for player 1, False for player 2
        self.pick = True  # True for picking phase, False for placing phase
        self.move_history: list[dict[str, str]] = []

        # Configuración de jugadores
        self.player1 = player1
        self.player2 = player2

        self.player_won: bool = False
        self.winner_name: str = self.TIE
        self.valid_moves = []

    def get_current_player(self):
        return self.player1 if self.turn else self.player2

    def get_next_player(self):
        return self.player2 if self.turn else self.player1

    @property
    def player_turn(self):
        return "Player 1" if self.turn else "Player 2"

    def play_turn(self):
        current_player = self.get_current_player()
        player_turn = "Player 1" if self.turn else "Player 2"

        if self.pick:
            # print(                f"\n{Fore.YELLOW}{player_turn} ({current_player.name}) está seleccionando una pieza..."            )

            valid_selection = False
            for n_tries in range(self.MAX_TRIES):
                selected_piece: Piece = current_player.select(self, n_tries)

                if coord := self.storage_board.find_piece(selected_piece):
                    _r_storage, _c_storage = coord  # en storage_board
                    valid_selection = True
                    break
                logger.debug(
                    f"Intento {n_tries + 1}: Seleccionando pieza {selected_piece}"
                )

            if not valid_selection:
                raise ValueError(f"Invalid selection after {self.MAX_TRIES} tries")

            # print(                f"{Fore.GREEN}Seleccionó la pieza: {selected_piece.__repr__(verbose=True)}"            )

            self.storage_board.remove_piece(_r_storage, _c_storage)
            self.selected_piece = selected_piece

            move_info = {
                "player": current_player.name,
                "action": "selected",
                "piece": self.selected_piece.__repr__(verbose=True),
                "position": None,
                "position_index": -1,
                "attempt": n_tries + 1,
                "piece_index": self.selected_piece.index(),
                "board": "",
            }
            self.move_history.append(move_info)
        else:
            # Colocar pieza
            # print(                f"\n{Fore.YELLOW}{player_turn} ({current_player.name} está colocando la pieza seleccionada..."            )

            valid_placement = False
            piece: Piece = self.selected_piece  # type: ignore
            assert isinstance(
                piece, Piece
            ), "Error, la lógica debería dar un tipo pieza"
            assert (
                piece not in self.game_board
            ), "Error, la pieza ya está en el tablero de juego"

            for n_tries in range(self.MAX_TRIES):
                row, col = current_player.place_piece(self, piece, n_tries)

                if self.game_board.is_empty(row, col):
                    valid_placement = True
                    break
                logger.debug(
                    f"Intento {n_tries + 1}: Colocando pieza en ({row}, {col})"
                )

            if not valid_placement:
                raise ValueError(f"Invalid selection after {self.MAX_TRIES} tries")

            # print(f"{Fore.GREEN}Colocó la pieza en posición ({row}, {col})")

            self.game_board.put_piece(piece, row, col)

            # # prueba de serialización y deserialización del tablero
            # logger.debug("Check serializing and deserializing the game board")
            # matrix = self.game_board.encode()
            # matrix = matrix.squeeze(0)
            # serial = self.game_board.serialize()
            # m2 = Board.deserialize(serial)
            # import numpy as np

            # logger.debug(matrix)
            # logger.debug(matrix.shape)
            # logger.debug(m2)
            # logger.debug(m2.shape)
            # assert np.array_equal(
            #     m2, matrix
            # ), "Error al serializar y deserializar el tablero"

            move_info = {
                "player": current_player.name,
                "action": "placed",
                "piece": piece.__repr__(verbose=False),
                "position": (row, col),
                "position_index": self.game_board.pos2index(row, col),
                "attempt": n_tries + 1,
                "piece_index": piece.index(),
                "board": self.game_board.serialize(),
            }
            self.move_history.append(move_info)

            # Verificar ganador
            if self.game_board.check_win():
                self.winner_name = current_player.name
                self.winner_pos = self.player_turn
                self.player_won = True
                # print(                    f"\n{Back.GREEN}{Fore.BLACK} ¡({self.player_turn}) {current_player.name} GANA LA PARTIDA! {Style.RESET_ALL}"                )
            elif self.game_board.is_full():
                self.winner_name = self.TIE
                # print(f"\n{Back.YELLOW}{Fore.BLACK} ¡EMPATE! {Style.RESET_ALL}")

            self.selected_piece = 0

        # Cambiar turno
        if self.pick:
            self.turn = not self.turn
        self.pick = not self.pick

    def show_history(self):
        """Muestra el historial de movimientos formateado en una tabla"""
        if not hasattr(self, "move_history") or not self.move_history:
            # print("No hay historial de movimientos disponible")
            return

        # Encabezado
        # print("\nHistorial de Movimientos:")
        # print("-" * 80)
        # print(            f"{'Mov.':<6} | {'Jugador':<15} | {'Acción':<10} | {'Pieza':<40} | {'Posición'}"        )
        # print("-" * 80)

        # Filas
        for i, move in enumerate(self.move_history, start=1):
            pieza = str(move.get("piece", "N/A")).replace(", ", " | ")
            pos = (
                f"({move['position'][0]}, {move['position'][1]})"
                if move.get("position")
                else "N/A"
            )
            # print(                f"{i:<6} | {move.get('player', 'N/A'):<15} | "                f"{move.get('action', 'N/A'):<10} | {pieza:<40} | {pos}")

    def export_history_to_csv(self, output_folder: str, match_number: int = 1):
        """Exporta el historial a un CSV con nombre que incluye match, fecha y hora"""
        # Crear directorio si no existe
        makedirs(output_folder, exist_ok=True)

        # Generar nombre de archivo con formato: MatchX_YYYY-MM-DD_HH-MM-SS.csv
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        filename = f"{current_time}_match{match_number:03d}.csv"

        filepath = path.join(output_folder, filename)

        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Movimiento",
                    "Jugador",
                    "Acción",
                    "Pieza",
                    "Pieza Index",
                    "Posición",
                    "Posición Index",
                    "Intento",
                    "Tablero",
                ]
            )

            # Escribir movimientos
            for i, move in enumerate(self.move_history, start=1):
                writer.writerow(
                    [
                        i,
                        move["player"],
                        move["action"],
                        move["piece"],
                        move["piece_index"],
                        (
                            f"({move['position'][0]}, {move['position'][1]})"
                            if move["position"]
                            else "N/A"
                        ),
                        move["position_index"],
                        move["attempt"],
                        move["board"],
                    ]
                )

        # print(f"\n{Fore.GREEN}Historial guardado en: {filepath}{Style.RESET_ALL}")
        return filepath

    def display_boards(self, exclude_footer: bool = False):
        """Muestra ambos tableros con formato mejorado"""

        current_player = self.get_next_player()
        action = "SELECCIONAR PIEZA" if self.pick else "COLOCAR PIEZA"

        if not self.pick:
            # Tablero de almacenamiento
            # print(f"\n{Fore.CYAN}=== PIEZAS DISPONIBLES ===")
            self.storage_board.print_board(self.selected_piece)
        else:
            # Tablero de juego principal
            # # print(f"{Fore.YELLOW}=== TABLERO DE JUEGO ===")
            self.game_board.print_board(self.selected_piece)

        # Pieza seleccionada
        if self.selected_piece:
            # print(                f"\n{Fore.GREEN}PIEZA SELECCIONADA: {self.selected_piece.__repr__(verbose=False)}"  # type: ignore            )
            pass
        # Movimientos válidos
        if not self.pick and hasattr(self, "valid_moves") and self.valid_moves:
            # print(                f"\n{Fore.MAGENTA}Posiciones válidas para colocar: {self.valid_moves}"            )
            pass
        if exclude_footer:
            return
        # Footer del turno
        # print(f"\n{Back.BLUE}{Fore.BLACK}{'='*60}{Style.RESET_ALL}")
        # print(            f"{Back.BLUE}{Fore.BLACK} TURNO ({self.player_turn}): {current_player.name} {Style.RESET_ALL}"        )
        # print(f"{Back.BLUE}{Fore.BLACK} ACCIÓN: {action.center(44)} {Style.RESET_ALL}")
        # print(f"{Back.BLUE}{Fore.BLACK}{'='*60}{Style.RESET_ALL}\n")
