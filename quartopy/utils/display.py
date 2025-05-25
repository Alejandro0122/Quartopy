from colorama import Fore, Back, Style
from ..game.board import Board
from ..game.piece import Coloration


def display_boards(self):
    """Muestra ambos tableros con formato mejorado"""
    current_player = self.get_current_player()
    action = "SELECCIONAR PIEZA" if self.pick else "COLOCAR PIEZA"

    # Encabezado del turno
    print(f"\n{Back.BLUE}{Fore.WHITE}{'='*60}{Style.RESET_ALL}")
    print(
        f"{Back.BLUE}{Fore.WHITE} TURNO: {current_player.name.center(46)} {Style.RESET_ALL}"
    )
    print(f"{Back.BLUE}{Fore.WHITE} ACCIÓN: {action.center(44)} {Style.RESET_ALL}")
    print(f"{Back.BLUE}{Fore.WHITE}{'='*60}{Style.RESET_ALL}\n")

    # Tablero de juego principal
    print(f"{Fore.YELLOW}=== TABLERO DE JUEGO ===")
    self.__print_board(self.game_board)

    # Tablero de almacenamiento
    print(f"\n{Fore.CYAN}=== PIEZAS DISPONIBLES ===")
    self.__print_board(self.storage_board)

    # Pieza seleccionada
    if self.selected_piece:
        print(
            f"\n{Fore.GREEN}PIEZA SELECCIONADA: {self.selected_piece.__repr__(verbose=True)}"
        )

    # Movimientos válidos si estamos en fase de colocación
    if not self.pick and self.valid_moves:
        print(f"\n{Fore.MAGENTA}Posiciones válidas para colocar: {self.valid_moves}")


def __print_board(self, board):
    """Método auxiliar para imprimir un tablero con formato"""
    # Encabezado de columnas
    print("    " + "   ".join(str(i) for i in range(board.cols)))

    # Borde superior
    print("  ╔" + "╦".join(["═══"] * board.cols) + "╗")

    for row in range(board.rows):
        # Contenido de la fila
        row_str = f"{row} ║"
        for col in range(board.cols):
            piece = board.get_piece(row, col)
            if piece == 0:
                row_str += "   ║"
            else:
                # Asignar colores diferentes a las piezas
                color = Fore.RED if piece.coloration == Coloration.BEIGE else Fore.BLUE
                row_str += f" {color}{piece}{Style.RESET_ALL} ║"
        print(row_str)

        # Borde entre filas
        if row < board.rows - 1:
            print("  ╠" + "╬".join(["═══"] * board.cols) + "╣")

    # Borde inferior
    print("  ╚" + "╩".join(["═══"] * board.cols) + "╝")
