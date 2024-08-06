from enum import Enum, auto

BG_COLOR = (128, 128, 128)
BLACK = (0, 0, 0)
BLUE = (0, 50, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

WINDOW_SIZE = 500
GRID_SIZE = 30
GRID_NUM = 15


class Stone(Enum):
    BLACK = auto()
    WHITE = auto()
    EMPTY = auto()

    def get_toggle_color(self):
        if self == Stone.EMPTY:
            return Stone.EMPTY

        if self == Stone.BLACK:
            return Stone.WHITE
        else:
            return Stone.BLACK
