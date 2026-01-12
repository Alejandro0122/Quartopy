from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QWidget, QLabel
from quartopy.gui.screens.start_screen import StartScreen
from quartopy.gui.screens.menu_screen import MenuScreen
from quartopy.gui.screens.game_board import GameBoard
from quartopy.gui.screens.type_player import TypePlayerScreen
from quartopy.gui.screens.record_screen import RecordScreen

class MainWindow(QMainWindow):
    """
    La ventana principal de la aplicación. Actúa como un gestor de pilas (Stack)
    para cambiar entre diferentes pantallas (Inicio, Menú, Tablero).
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Juego Quarto')
        self.showFullScreen()
        
        # Crea el QStackedWidget que contendrá todas las pantallas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Inicializa las pantallas
        self.start_screen = StartScreen()
        self.menu_screen = MenuScreen()
        self.game_board = None # Se creará dinámicamente
        self.type_player = TypePlayerScreen()
        self.record_screen = RecordScreen()

        # Añade las pantallas al StackedWidget
        # Guardamos un índice para referenciar cada pantalla:
        self.stacked_widget.addWidget(self.start_screen) # Índice 0: Pantalla de Inicio
        self.stacked_widget.addWidget(self.menu_screen)  # Índice 1: Pantalla de Menú
        self.stacked_widget.addWidget(self.record_screen) # Añadido para la pantalla de records

        # Conexiones: Conecta la señal de la pantalla de inicio a la función de navegación
        self.start_screen.start_button.clicked.connect(self.show_menu)
        self.start_screen.exit_button.clicked.connect(self.close)
        
        # Conexiones de MenuScreen
        self.menu_screen.btn_exit.clicked.connect(self.close)
        self.menu_screen.btn_play.clicked.connect(self.type_player.show)
        self.menu_screen.btn_record.clicked.connect(self.show_record_screen) # Conexión para los records
        self.menu_screen.btn_rules.clicked.connect(self.video_rules)

        # Conexiones de otras pantallas
        self.record_screen.back_to_menu.connect(self.show_menu)
        self.type_player.back_btn.clicked.connect(self.closeMini1)
        self.type_player.players_selected.connect(self.start_game_with_config)


        # Muestra la pantalla inicial al comenzar
        self.stacked_widget.setCurrentIndex(0) # Muestra la StartScreen
        

    def show_menu(self):
        """Muestra la pantalla del menú (Índice 1)."""
        self.stacked_widget.setCurrentWidget(self.menu_screen)
        
    def show_start(self):
        """Muestra la pantalla de inicio (Índice 0)."""
        self.stacked_widget.setCurrentIndex(0)

    def show_record_screen(self):
        """Muestra la pantalla de records."""
        self.stacked_widget.setCurrentWidget(self.record_screen)

    def show_game(self):
        """Muestra la pantalla del tablero de juego (Índice 2)."""
        self.stacked_widget.setCurrentIndex(2)
        if self.game_board and hasattr(self.game_board, 'view'):
            # Desactiva la barra de desplazamiento horizontal
            self.game_board.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            # Desactiva la barra de desplazamiento vertical
            self.game_board.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def start_game_with_config(self, config: dict):
        
        self.type_player.close()
        
        """
        Crea una nueva instancia de GameBoard con la configuración de jugadores
        y modo 2x2 seleccionada, y la muestra.
        """
        player1_type = config['player1']
        player2_type = config['player2']
        player1_name = config['player1_name']
        player2_name = config['player2_name']
        mode_2x2 = config['mode_2x2']

        # Remover el GameBoard antiguo si existe
        if self.game_board:
            # Asegurarse de que el widget no sea None antes de intentar removerlo
            if self.stacked_widget.indexOf(self.game_board) != -1:
                self.stacked_widget.removeWidget(self.game_board)
            self.game_board.deleteLater() # Asegura que el objeto sea eliminado
        
        # Crear nueva instancia de GameBoard con la configuración
        self.game_board = GameBoard(
            parent=self, 
            player1_type=player1_type, 
            player2_type=player2_type,
            player1_name=player1_name,
            player2_name=player2_name,
            mode_2x2=mode_2x2
        )
        # Re-conectar la señal para volver al menú
        self.game_board.back_to_menu_signal.connect(self.show_menu)

        self.stacked_widget.addWidget(self.game_board)
        self.stacked_widget.setCurrentWidget(self.game_board) # Mostrar el nuevo GameBoard
        
        if self.game_board and hasattr(self.game_board, 'view'):
            self.game_board.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.game_board.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def video_rules(self):
        """Muestra las reglas del juego en un video."""
        import webbrowser
        webbrowser.open('https://www.tiktok.com/@silvermangaming/video/7442747523795520823')  # Reemplaza con el enlace correcto
        
    # (A futuro, aquí pondremos métodos para show_game, show_rules, etc.)

    def closeMini1(self):
        """Cierra la ventana de records."""
        self.type_player.hide()