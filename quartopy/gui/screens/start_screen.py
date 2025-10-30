# quarto_py/gui/screens/start_screen.py

from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt  

class StartScreen(QWidget):
    # ... (El código de __init__ debe lucir así:)
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. Configuración básica de la ventana (Estos valores son ignorados,
        #    ya que ahora MainWindow controla el tamaño, pero se dejan por si acaso)
        self.setWindowTitle('Quarto - Inicio')
        self.setGeometry(100, 100, 400, 300) 
        
        # 2. Crea el Layout (diseño) principal
        layout = QVBoxLayout()
        
        # 3. Crea los Widgets
        
        title_label = QLabel("¡Bienvenido al Juego Quarto!")
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)# Qt.AlignCenter
        
        # El botón - IMPORTANTE: No lo conectamos aquí
        self.start_button = QPushButton('Comenzar a Jugar')
        
        # 4. Añade los Widgets al Layout
        layout.addWidget(title_label)
        layout.addWidget(self.start_button)
        
        layout.addStretch(1)
        
        # 5. Aplica el Layout a la ventana
        self.setLayout(layout)

    # ❗ ELIMINA EL MÉTODO 'on_start_clicked' DE AQUÍ ❗
    # La conexión ahora se gestiona en main_window.py