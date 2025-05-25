from .piece import Piece
from .piece import Coloration, Shape, Size, Hole
import numpy as np


class Board:
    def __init__(self, name, storage, rows, cols):
        self.name = name
        self.storage = storage
        self.board: list[list[Piece | int]] = [
            [0 for _ in range(cols)] for _ in range(rows)
        ]
        self.rows = rows
        self.cols = cols

        if self.storage:
            self.__init_pieces()

    def __init_pieces(self):
        row = 0
        for c in Coloration:
            col = 0
            for h in Hole:
                for sh in Shape:
                    for si in Size:
                        self.board[row][col] = Piece(row, col, c, sh, si, h)
                        col += 1
            row += 1

    def get_piece(self, row, col) -> Piece | int:
        return self.board[row][col]

    def put_piece(self, piece, row, col):
        # Solo asignar si es una Pieza o 0 (vacío)
        if isinstance(piece, Piece) or piece == 0:
            self.board[row][col] = piece
            if piece != 0:
                piece.row = row
                piece.col = col
        else:
            raise ValueError("Solo se pueden colocar objetos Piece o 0 (vacío)")

    def copy(self):
        """Crea una copia profunda del tablero"""
        new_board = Board(self.name, False, self.rows, self.cols)
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.get_piece(row, col)
                if isinstance(piece, Piece):
                    new_board.put_piece(piece.copy(), row, col)
                else:
                    new_board.put_piece(0, row, col)
        return new_board

    def move_to_gameboard(self, game_board, piece, row, col):
        try:
            self.board[piece.row][piece.col] = 0
            game_board.put_piece(piece, row, col)
            return piece
        except AttributeError:
            print("Tipo no válido.")

    def winner(self):
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
        moves = []
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.get_piece(row, col)
                if not self.storage:
                    if piece == 0:
                        moves.append((row, col))
                else:
                    if piece != 0:
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
                piece = self.get_piece(r, c)

                if isinstance(piece, Piece):
                    B[:, :, r, c] = piece.vectorize()
                # else:
                # continue

        return B

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
