from .piece import Piece
from .piece import Coloration, Shape, Size, Hole

import numpy as np
from colorama import Fore, Style, Back


class Board:
    def __init__(self, name: str, storage: bool, rows, cols):
        self.name = name
        self.storage = storage  # Cuando True crea un board con las piezas disponibles
        self.board: list[list[Piece | int]] = [
            [0 for _ in range(cols)] for _ in range(rows)
        ]
        self.rows: int = rows
        self.cols: int = cols

        if self.storage:
            self.__init_pieces()

    def __init_pieces(self):
        """Crea un board con todas las piezas posibles"""
        row = 0
        for si in Size:
            col = 0
            for c in Coloration:
                for sh in Shape:
                    for h in Hole:
                        self.board[row][col] = Piece(si, c, sh, h)
                        col += 1
            row += 1

    def get_piece(self, row, col) -> Piece:
        """Retorna la pieza en la posición (row, col) del tablero.
        Se asume que la posición es válida.
        Debe retornar Piece"""
        assert isinstance(
            self.board[row][col], Piece
        ), "No se puede hacer get_piece en una posición vacía"
        return self.board[row][col]

    def is_empty(self, row: int, col: int) -> bool:
        """Retorna True si la posición (row, col) está vacía (0)"""
        return self.board[row][col] == 0

    def find_piece(self, piece: Piece) -> tuple[int, int] | None:
        """Busca una pieza en el tablero y retorna su posición (row, col)
        Si no la encuentra, retorna None"""
        if isinstance(piece, Piece):
            for row in range(self.rows):
                for col in range(self.cols):
                    if self.board[row][col] == piece:
                        return row, col
            return None
        else:
            raise ValueError("El item debe ser una pieza")

    def remove_piece(self, row: int, col: int):
        """Elimina una pieza del tablero.
        Solo es válido cuando ``storage`` = True"""
        assert (
            self.storage
        ), "Solo se puede eliminar piezas de un tablero de tipo storage"

        assert isinstance(self.board[row][col], Piece), "El item debe ser una pieza"

        self.board[row][col] = 0

    def put_piece(self, piece: Piece | int, row, col):
        # Solo asignar si es una Pieza o 0 (vacío)
        if isinstance(piece, Piece):  # or piece == 0:
            self.board[row][col] = piece
        else:
            raise ValueError("Solo se pueden colocar objetos Piece o 0 (vacío)")

    def check_win(self):
        """Retorna True si hay un ganador, False en caso contrario"""
        if self.__check_all_lines():
            return True
        return False

    def is_full(self):
        for row in range(self.rows):
            if 0 in self.board[row]:
                return False
        return True

    def __is_winning_line(self, pieces):
        if 0 in pieces:
            return False
        p = pieces[0]
        ho, si, sh, co = True, True, True, True
        for piece in pieces:
            ho = p.hole == piece.hole and ho
            si = p.size == piece.size and si
            sh = p.shape == piece.shape and sh
            co = p.coloration == piece.coloration and co
        return ho or si or sh or co

    def __check_all_lines(self):
        # Check rows
        for row in range(self.rows):
            if not (0 in self.board[row]):
                if self.__is_winning_line(self.board[row]):
                    return True

        # Check columns
        for col in range(self.cols):
            pieces = []
            for row in range(self.rows):
                pieces.append(self.board[row][col])
            if not (0 in pieces):
                if self.__is_winning_line(pieces):
                    return True

        # Check diagonals (only if square board)
        if self.cols == self.rows:
            pieces = []
            pieces2 = []
            for col in range(self.cols):
                pieces.append(self.board[col][col])
                pieces2.append(self.board[col][self.cols - col - 1])
            if not (0 in pieces):
                if self.__is_winning_line(pieces):
                    return True
            if not (0 in pieces2):
                if self.__is_winning_line(pieces2):
                    return True
        return False

    def get_valid_moves(self):
        moves: list[tuple[int, int]] = []
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.board[row][col]
                if self.storage:
                    if piece != 0:
                        # Piezas que están en storage
                        moves.append((row, col))
                else:
                    if piece == 0:
                        # Espacios vacíos
                        moves.append((row, col))
        return moves

    def __repr__(self):
        s = f"{self.name}:\n"
        for x in range(self.rows):
            for y in range(self.cols):
                s += (
                    ((str(self.board[x][y]) + " "))
                    if self.board[x][y] != 0
                    else "---- "
                )
            s += "\n"
        return s

    ####################################################################
    def to_matrix(self):
        """Convierte el tablero en una matriz de dimensiones
        (batch=1, dims, rows, cols)
        """

        # dims (Tamaño, Color, Forma, Hueco)
        B = np.zeros((1, 4, self.rows, self.cols))
        for r in range(self.rows):
            for c in range(self.cols):
                piece = self.board[r][c]

                if isinstance(piece, Piece):
                    B[:, :, r, c] = piece.vectorize()
                # else:
                # continue

        return B

    # ##############################################################
    def __contains__(self, item: Piece):
        """Retorna True si el item es una pieza del tablero"""
        if isinstance(item, Piece):
            for row in range(self.rows):
                for col in range(self.cols):
                    if self.board[row][col] == item:
                        return True
            return False
        else:
            raise ValueError("El item debe ser una pieza")

    @staticmethod
    # ##############################################################
    def to_matrix_batch(boards: list["Board"]):
        """Convierte una lista de tableros en una matriz de dimensiones
        (batch, dims, rows, cols)

        Asume todos los tableros tienen el mismo tamaño.
        """
        B = np.zeros((len(boards), 4, boards[0].rows, boards[0].cols))
        for i, board in enumerate(boards):
            B[i, :, :, :] = board.to_matrix()
        return B

    def print_board(self, piece_highlight: Piece | int = 0):
        """Método auxiliar para imprimir un tablero con formato"""

        # Encabezado de columnas
        print("    " + "      ".join(str(i) for i in range(self.cols)))

        # Borde superior
        print("  ╔" + "╦".join(["══════"] * self.cols) + "╗")

        for row in range(self.rows):
            # Contenido de la fila
            row_str = f"{row} ║"
            for col in range(self.cols):
                piece = self.board[row][col]
                if isinstance(piece, Piece):
                    if piece == piece_highlight:
                        # Resaltar la pieza seleccionada
                        back = Back.YELLOW
                    else:
                        back = Back.RESET
                    color = (
                        Fore.RED if piece.coloration == Coloration.BLACK else Fore.BLUE
                    )
                    row_str += f" {back}{color}{piece}{Style.RESET_ALL} ║"
                else:
                    row_str += "      ║"
            print(row_str)

            # Borde entre filas
            if row < self.rows - 1:
                print("  ╠" + "╬".join(["══════"] * self.cols) + "╣")

        # Borde inferior
        print("  ╚" + "╩".join(["══════"] * self.cols) + "╝")
