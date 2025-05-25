from enum import Enum
import numpy as np


class Size(Enum):
    LITTLE = "LITTLE"
    TALL = "TALL"


class Coloration(Enum):
    BEIGE = "BEIGE"
    BROWN = "BROWN"


class Shape(Enum):
    CIRCLE = "CIRCLE"
    SQUARE = "SQUARE"


class Hole(Enum):
    WITHOUT = "WITHOUT_HOLE"
    WITH = "WITH_HOLE"


class Piece:
    def __init__(self, row, col, size, coloration, shape, hole):
        if not isinstance(size, Size):
            raise ValueError("size must be a Size enum")
        if not isinstance(coloration, Coloration):
            raise ValueError("coloration must be a Coloration enum")
        if not isinstance(shape, Shape):
            raise ValueError("shape must be a Shape enum")
        if not isinstance(hole, Hole):
            raise ValueError("hole must be a Hole enum")

        self.row = row
        self.col = col
        self.coloration = coloration
        self.shape = shape
        self.size = size
        self.hole = hole

    def __repr__(self, verbose=False):
        if verbose:
            return f"{self.size.value}, {self.coloration.value}, {self.shape.value}, {self.hole.value}"
        else:
            return f"{'T' if self.size == Size.TALL else 'S'}{'B' if self.coloration == Coloration.BEIGE else 'D'}{'C' if self.shape == Shape.CIRCLE else 'Q'}{'H' if self.hole == Hole.WITH else 'N'}"

    # ####################################################################
    def vectorize(self) -> np.ndarray:
        """Convierte la pieza en un vector booleano de 4 dimensiones, donde cada dimensión representa una propiedad de la pieza.

        ## Return
        np.array de (tamaño, color, forma y agujero).
        * Tamaño 0 = LITTLE, 1 = TALL
        * Color 0 = BEIGE, 1 = BROWN
        * Forma 0 = CIRCLE, 1 = SQUARE
        * Agujero 0 = WITHOUT_HOLE, 1 = WITH_HOLE
        """
        v = [
            1 if self.size == Size.TALL else 0,
            1 if self.coloration == Coloration.BROWN else 0,
            1 if self.shape == Shape.SQUARE else 0,
            1 if self.hole == Hole.WITH else 0,
        ]
        return np.array(v, dtype=float).reshape((1, 4))

    def copy(self):
        """Crea una copia de la pieza"""
        return Piece(
            self.row, self.col, self.size, self.coloration, self.shape, self.hole
        )

    # ####################################################################
    def vectorize_onehot(self) -> np.ndarray:
        """Convierte la pieza en un vector one-hot encoded.

        ## Return

        ``vector``: np.array (16, )
        """
        vector = np.zeros((2, 2, 2, 2), dtype=float)
        print(vector.shape)
        vector[
            int(self.size == Size.TALL),
            int(self.coloration == Coloration.BROWN),
            int(self.shape == Shape.SQUARE),
            int(self.hole == Hole.WITH),
        ] = 1.0
        print(vector)
        vector = vector.flatten()
        return vector

    # ####################################################################
    @classmethod
    def from_onehot(cls, vector: np.ndarray, rc: np.ndarray | list[int]) -> "Piece":
        """Convierte un vector one-hot encoded en una pieza.
        ## Parameters

        ``vector``: np.array (16, )
        ``rc``: np.array (2, )

        ## Return
        ``piece``: Piece
        """
        if vector.shape != (16,):
            raise ValueError("vector must be of shape (16,)")
        if not np.all(np.isin(vector, [0, 1])):
            raise ValueError("vector must be binary")
        if not np.sum(vector) == 1:
            raise ValueError("vector must be one-hot encoded")

        if len(rc) != 2:
            raise ValueError("rc must be of shape (2,)")

        vector = vector.reshape((2, 2, 2, 2))

        coords = np.argwhere(vector == 1)[0]
        size = Size.LITTLE if coords[0] == 0 else Size.TALL
        coloration = Coloration.BEIGE if coords[1] == 0 else Coloration.BROWN
        shape = Shape.CIRCLE if coords[2] == 0 else Shape.SQUARE
        hole = Hole.WITHOUT if coords[3] == 0 else Hole.WITH

        piece = cls(rc[0], rc[1], size, coloration, shape, hole)
        return piece

    @classmethod
    # ####################################################################
    def from_index(cls, piece_idx: int, rc_idx: int) -> "Piece":
        """Convierte un índice de pieza en una pieza.
        ## Parameters
        ``piece_idx``: int [0, 15]
        ``rc_idx``: int [0, 15]

        ## Return
        ``piece``: Piece
        """
        if piece_idx < 0 or piece_idx > 15:
            raise ValueError("piece_idx must be between 0 and 15")
        if rc_idx < 0 or rc_idx > 15:
            raise ValueError("rc_idx must be between 0 and 15")
        # Convertir el índice de pieza en un vector one-hot encoded
        vector = np.zeros((16,), dtype=float)
        vector[piece_idx] = 1.0
        # Convertir el vector one-hot encoded en una pieza
        piece = cls.from_onehot(vector, [rc_idx // 4, rc_idx % 4])
        return piece
