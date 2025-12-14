from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QWidget, QLabel
from quartopy.gui.screens.start_screen import StartScreen
from quartopy.gui.screens.menu_screen import MenuScreen
from quartopy.gui.screens.game_board import GameBoard

class MainWindow(QMainWindow):
    """
    La ventana principal de la aplicación. Actúa como un gestor de pilas (Stack)
    para cambiar entre diferentes pantallas (Inicio, Menú, Tablero).
    """
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setWindowTitle('Juego Quarto')
        self.setGeometry(180, 150, 1000, 500)

        self.title_bar = QWidget(self)
        self.title_bar.setGeometry(0, 0, self.width(), 30)
        self.title_bar.setStyleSheet("background-color: black;")
        
        # 4. Colocar el título del juego en esta barra
        self.custom_title_label = QLabel("Juego Quarto", self.title_bar)
        self.custom_title_label.setStyleSheet("color: white; font-weight: bold;")
        self.custom_title_label.move(5, 5) # Pequeño margen
        
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
        self.start_screen.exit_button.clicked.connect(self.close)
        self.game_board.btn_exit.clicked.connect(self.close)

        # Conexión para el botón Jugar del Menú
        self.menu_screen.btn_play.clicked.connect(self.show_game)

        # Muestra la pantalla inicial al comenzar
        self.stacked_widget.setCurrentIndex(0) # Muestra la StartScreen

        # Conexión para video de reglas
        self.menu_screen.btn_rules.clicked.connect(self.video_rules)
        

    def show_menu(self):
        """Muestra la pantalla del menú (Índice 1)."""
        self.stacked_widget.setCurrentIndex(1)
        
    def show_start(self):
        """Muestra la pantalla de inicio (Índice 0)."""
        self.stacked_widget.setCurrentIndex(0)

    def show_game(self):
        """Muestra la pantalla del tablero de juego (Índice 2)."""
        self.setFixedSize(930, 600)
        self.move(250, 100)
        self.stacked_widget.setCurrentIndex(2)
        if self.game_board and hasattr(self.game_board, 'view'):
            # Desactiva la barra de desplazamiento horizontal
            self.game_board.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            # Desactiva la barra de desplazamiento vertical
            self.game_board.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def video_rules(self):
        """Muestra las reglas del juego en un video."""
        import webbrowser
        webbrowser.open('https://www.tiktok.com/@silvermangaming/video/7442747523795520823')  # Reemplaza con el enlace correcto
        
    # (A futuro, aquí pondremos métodos para show_game, show_rules, etc.)