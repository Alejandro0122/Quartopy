from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QApplication
from PyQt5.QtGui import QFont, QGuiApplication, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
import importlib.util
import importlib.machinery
from quartopy import BotAI
import os

class AddBotScreen(QDialog):
    bot_added_successfully = pyqtSignal(dict) # New signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon('quartopy/gui/assets/images/robot_icon.png'))
        #self.setWindowFlags(Qt.FramelessWindowHint) # Ocultar la barra de título
        self.setWindowTitle("Agregar Nuevo Bot")
        self.setFixedSize(500, 300) # Adjusted size for new elements
        self.setStyleSheet("background-color: #2a2a2a; color: white;") # Removed black border
        self.setWindowModality(Qt.ApplicationModal)
        self.bot_file_path = None # Initialize
        self.model_file_path = None # Initialize
        
        self.setup_ui() # Call setup_ui first to finalize layout

        # Centrar la ventana
        # Ensure layout is computed before moving
        self.adjustSize() 
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.width()) / 2
        y = (screen_geometry.height() - self.height()) / 2
        self.move(int(x), int(y))

        self.save_btn.setEnabled(False) # Initially disable save button

    def showEvent(self, event):
        super().showEvent(event)
        # Centrar la ventana una vez que sus dimensiones son definitivas
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.width()) / 2
        y = (screen_geometry.height() - self.height()) / 2
        self.move(int(x), int(y))


    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        title_label = QLabel("Configuración de Nuevo Bot")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        #self.setWindowFlags(Qt.FramelessWindowHint)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #FFD700;")
        main_layout.addWidget(title_label)
        
        main_layout.addStretch() # Flexible space after title

        file_selection_layout = QVBoxLayout()
        file_selection_layout.setSpacing(10)

        # Cargar Bot
        bot_file_layout = QHBoxLayout()
        bot_file_label = QLabel("Cargar Bot:")
        bot_file_label.setFont(QFont("Arial", 10))
        bot_file_layout.addWidget(bot_file_label)
        
        self.bot_path_label = QLabel("No se ha seleccionado archivo")
        self.bot_path_label.setFont(QFont("Arial", 9))
        self.bot_path_label.setStyleSheet("color: #CCCCCC;")
        bot_file_layout.addWidget(self.bot_path_label)

        self.load_bot_btn = QPushButton("Examinar")
        self.load_bot_btn.setFont(QFont("Arial", 9, QFont.Bold))
        self.load_bot_btn.setFixedSize(80, 25)
        self.load_bot_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: 1px solid #0056b3;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
                border: 1px solid #003F7F;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        self.load_bot_btn.clicked.connect(self._open_bot_file_dialog)
        bot_file_layout.addWidget(self.load_bot_btn)
        bot_file_layout.addStretch()
        file_selection_layout.addLayout(bot_file_layout)

        # Cargar Modelo
        model_file_layout = QHBoxLayout()
        model_file_label = QLabel("Cargar Modelo:")
        model_file_label.setFont(QFont("Arial", 10))
        model_file_layout.addWidget(model_file_label)
        
        self.model_path_label = QLabel("No se ha seleccionado archivo")
        self.model_path_label.setFont(QFont("Arial", 9))
        self.model_path_label.setStyleSheet("color: #CCCCCC;")
        model_file_layout.addWidget(self.model_path_label)

        self.load_model_btn = QPushButton("Examinar")
        self.load_model_btn.setFont(QFont("Arial", 9, QFont.Bold))
        self.load_model_btn.setFixedSize(80, 25)
        self.load_model_btn.setStyleSheet(self.load_bot_btn.styleSheet()) # Re-use style
        self.load_model_btn.clicked.connect(self._open_model_file_dialog)
        model_file_layout.addWidget(self.load_model_btn)
        model_file_layout.addStretch()
        file_selection_layout.addLayout(model_file_layout)

        main_layout.addLayout(file_selection_layout)
        
        main_layout.addStretch() # Flexible space before buttons

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.close_btn = QPushButton("Cerrar")
        self.close_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.close_btn.setFixedSize(100, 35)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: 2px solid #777777;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #666666;
                border: 2px solid #888888;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        
        # New Verify Button
        self.verify_btn = QPushButton("Verificar")
        self.verify_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.verify_btn.setFixedSize(100, 35)
        self.verify_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: 2px solid #0056b3;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #0056b3;
                border: 2px solid #003F7F;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        self.verify_btn.clicked.connect(self._verify_bot_config)

        self.save_btn = QPushButton("Guardar")
        self.save_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.save_btn.setFixedSize(100, 35)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: black;
                border: 2px solid #FFC400;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #FFC400;
                border: 2px solid #FFB300;
            }
            QPushButton:pressed {
                background-color: #FFB300;
            }
            QPushButton:disabled {
                background-color: #A0A000; /* Opaque yellow */
                color: #555555; /* Darker text */
                border: 2px solid #808000;
            }
        """)
        self.save_btn.clicked.connect(self._save_bot_config)

        buttons_layout.addWidget(self.close_btn)
        buttons_layout.addWidget(self.verify_btn) # Add verify button
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)

    def _perform_bot_validation(self, bot_file_path, model_file_path):
        """Encapsula la lógica de validación del bot y el modelo."""
        # Ensure save button is disabled by default, will be enabled on successful validation
        self.save_btn.setEnabled(False)

        if not bot_file_path:
            return False, "Por favor, selecciona un archivo de Bot (.py).", None

        bot_name = ""
        try:
            # Dynamically load the module
            spec = importlib.util.spec_from_file_location("dynamic_bot_module", bot_file_path)
            if spec is None:
                raise ImportError(f"No se pudo crear la especificación para {bot_file_path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            bot_class = None
            # Find a class that inherits from BotAI in the loaded module
            for name, obj in vars(module).items():
                if isinstance(obj, type) and issubclass(obj, BotAI) and obj is not BotAI:
                    bot_class = obj
                    break

            if bot_class is None:
                raise ValueError("No se encontró una clase de Bot válida (subclase de BotAI) en el archivo.")

            # Try to instantiate the bot to get its name and validate model_path if needed
            # For CNNBot-like bots, model_path is passed here
            # We'll pass a temporary name for instantiation
            if model_file_path:
                temp_bot_instance = bot_class(name=f"{os.path.basename(bot_file_path)}_temp", model_path=model_file_path)
            else:
                # Some bots might not require a model path
                temp_bot_instance = bot_class(name=f"{os.path.basename(bot_file_path)}_temp")
            bot_name = temp_bot_instance.name

            bot_config = {
                'bot_name': bot_name,
                'bot_class': bot_class,
                'model_path': model_file_path
            }
            return True, f"Bot '{bot_name}' parece ser válido.", bot_config

        except Exception as e:
            return False, f"Error al validar el bot: {e}", None

    def _open_bot_file_dialog(self):
        self.save_btn.setEnabled(False) # Disable save button on file change
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo de Bot", "", "Python Files (*.py);;All Files (*)")
        if file_path:
            self.bot_file_path = file_path
            self.bot_path_label.setText(os.path.basename(file_path))
        else:
            self.bot_file_path = None
            self.bot_path_label.setText("No se ha seleccionado archivo")

    def _open_model_file_dialog(self):
        self.save_btn.setEnabled(False) # Disable save button on file change
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo de Modelo", "", "PyTorch Models (*.pt);;All Files (*)")
        if file_path:
            self.model_file_path = file_path
            self.model_path_label.setText(os.path.basename(file_path))
        else:
            self.model_file_path = None
            self.model_path_label.setText("No se ha seleccionado archivo")

    def _verify_bot_config(self):
        """Verifica la configuración del bot sin guardarla."""
        is_valid, message, _ = self._perform_bot_validation(self.bot_file_path, self.model_file_path)
        if is_valid:
            QMessageBox.information(self, "Verificación Exitosa", message)
            self.save_btn.setEnabled(True) # Enable save button on successful verification
        else:
            QMessageBox.warning(self, "Error de Verificación", message)
            self.save_btn.setEnabled(False) # Ensure it's disabled on failure

    def _save_bot_config(self):
        """Guarda la configuración del bot si es válida."""
        is_valid, message, bot_config = self._perform_bot_validation(self.bot_file_path, self.model_file_path)
        if is_valid:
            self.bot_added_successfully.emit(bot_config)
            QMessageBox.information(self, "Éxito", f"Bot '{bot_config['bot_name']}' cargado exitosamente.")
            self.accept() # Close dialog on success
        else:
            QMessageBox.critical(self, "Error al Guardar Bot", message)