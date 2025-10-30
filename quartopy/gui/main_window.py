# quarto_py/gui/main_window.py

from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from .screens.start_screen import StartScreen
from .screens.menu_screen import MenuScreen
from .screens.game_board import GameBoard

class MainWindow(QMainWindow):
    """
    La ventana principal de la aplicación. Actúa como un gestor de pilas (Stack)
    para cambiar entre diferentes pantallas (Inicio, Menú, Tablero).
    """
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Juego Quarto')
        self.setGeometry(100, 100, 600, 500)
        
        # Crea el QStackedWidget que contendrá todas las pantallas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Inicializa las pantallas
        self.start_screen = StartScreen()
        self.menu_screen = MenuScreen()
        self.game_board = GameBoard()
        
        # Añade las pantallas al StackedWidget
        # Guardamos un índice para referenciar cada pantalla:
        self.stacked_widget.addWidget(self.start_screen) # Índice 0: Pantalla de Inicio
        self.stacked_widget.addWidget(self.menu_screen)  # Índice 1: Pantalla de Menú
        self.stacked_widget.addWidget(self.game_board)
        
        # Conexiones: Conecta la señal de la pantalla de inicio a la función de navegación
        self.start_screen.start_button.clicked.connect(self.show_menu)
        
        # Conexión para el botón Salir del Menú
        self.menu_screen.btn_exit.clicked.connect(self.close)

        # Conexión para el botón Jugar del Menú
        self.menu_screen.btn_play.clicked.connect(self.show_game)

        # Muestra la pantalla inicial al comenzar
        self.stacked_widget.setCurrentIndex(0) # Muestra la StartScreen

    def show_menu(self):
        """Muestra la pantalla del menú (Índice 1)."""
        self.stacked_widget.setCurrentIndex(1)
        
    def show_start(self):
        """Muestra la pantalla de inicio (Índice 0)."""
        self.stacked_widget.setCurrentIndex(0)

    def show_game(self):
        """Muestra la pantalla del tablero de juego (Índice 2)."""
        self.stacked_widget.setCurrentIndex(2)

        
    # (A futuro, aquí pondremos métodos para show_game, show_rules, etc.)