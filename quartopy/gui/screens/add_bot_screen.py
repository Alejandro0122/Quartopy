from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QApplication
from PyQt5.QtGui import QFont, QGuiApplication, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
import importlib.util
import importlib.machinery
from quartopy import BotAI
import os
import sys # Added this import
import shutil # Added this import

class AddBotScreen(QDialog):
    bot_added_successfully = pyqtSignal(dict) # New signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon('quartopy/gui/assets/images/robot_icon.png'))
        #self.setWindowFlags(Qt.FramelessWindowHint) # Ocultar la barra de título
        self.setWindowTitle("Agregar Nuevo Bot")
        self.setFixedSize(500, 350) # Adjusted size for new elements
        self.setStyleSheet("background-color: #2a2a2a; color: white;") # Removed black border
        self.setWindowModality(Qt.ApplicationModal)
        self.bot_file_path = None # Initialize
        self.model_file_path = None # Initialize
        self.weights_file_path = None # Initialize weights file path
        
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

        # Cargar Modelo
        model_file_layout = QHBoxLayout()
        model_file_label = QLabel("Cargar Modelo para CNN Bot:")
        model_file_label.setFont(QFont("Arial", 10))
        model_file_layout.addWidget(model_file_label)
        
        self.model_path_label = QLabel("No se ha seleccionado archivo")
        self.model_path_label.setFont(QFont("Arial", 9))
        self.model_path_label.setStyleSheet("color: #CCCCCC;")
        model_file_layout.addWidget(self.model_path_label)

        self.load_model_btn = QPushButton("Examinar")
        self.load_model_btn.setFont(QFont("Arial", 9, QFont.Bold))
        self.load_model_btn.setFixedSize(80, 25)
        self.load_model_btn.setStyleSheet("""
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
        self.load_model_btn.clicked.connect(self._open_model_file_dialog)
        model_file_layout.addWidget(self.load_model_btn)
        model_file_layout.addStretch()
        file_selection_layout.addLayout(model_file_layout)

        # Cargar Pesos
        weights_file_layout = QHBoxLayout()
        weights_file_label = QLabel("Cargar Pesos (.pt):")
        weights_file_label.setFont(QFont("Arial", 10))
        weights_file_layout.addWidget(weights_file_label)
        
        self.weights_path_label = QLabel("No se ha seleccionado archivo")
        self.weights_path_label.setFont(QFont("Arial", 9))
        self.weights_path_label.setStyleSheet("color: #CCCCCC;")
        weights_file_layout.addWidget(self.weights_path_label)

        self.load_weights_btn = QPushButton("Examinar")
        self.load_weights_btn.setFont(QFont("Arial", 9, QFont.Bold))
        self.load_weights_btn.setFixedSize(80, 25)
        self.load_weights_btn.setStyleSheet("""
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
        self.load_weights_btn.clicked.connect(self._open_weights_file_dialog)
        weights_file_layout.addWidget(self.load_weights_btn)
        weights_file_layout.addStretch()
        file_selection_layout.addLayout(weights_file_layout)

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
        self.verify_btn.setEnabled(False) # Initially disable verify button

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

    def _perform_bot_validation(self, model_file_path, weights_file_path):
        """Encapsula la lógica de validación del bot CNN y el modelo."""
        self.save_btn.setEnabled(False)

        if not model_file_path:
            return False, "Por favor, selecciona un archivo de Modelo (.py).", None
        if not weights_file_path:
            return False, "Por favor, selecciona un archivo de Pesos (.pt).", None
        if not os.path.exists(weights_file_path):
            return False, f"El archivo de pesos no se encuentra en {weights_file_path}.", None

        quartopy_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        
        # Add project root to sys.path to resolve absolute imports like 'from quartopy.x.y import Z'
        if quartopy_root not in sys.path:
            sys.path.insert(0, quartopy_root)
        
        model_class = None
        bot_class = None
        temp_sys_path_added = False # Flag to track if we added quartopy_root to sys.path
        
        try:
            temp_sys_path_added = True

            # Import CNNBot directly from its known package path
            from quartopy.bot.CNN_bot import CNNBot as bot_class_imported
            bot_class = bot_class_imported

            if bot_class is None: # Should not happen if import is successful
                raise ValueError("No se encontró la clase CNNBot en quartopy.bot.CNN_bot.")

            # Determine the absolute module name for the model file
            # e.g., quartopy/models/CNN_uncoupled.py -> quartopy.models.CNN_uncoupled
            relative_model_path = os.path.relpath(model_file_path, quartopy_root)
            if not relative_model_path.startswith('quartopy'):
                raise ImportError(f"El archivo del modelo {model_file_path} no parece estar dentro del paquete 'quartopy'.")
            
            model_module_name = relative_model_path.replace(os.sep, '.')[:-3] # Remove .py
            
            # Use importlib.import_module for the model
            module_model = importlib.import_module(model_module_name)

            candidate_classes = [obj for name, obj in vars(module_model).items() 
                                 if isinstance(obj, type) and obj.__module__ == module_model.__name__]
            
            if not candidate_classes:
                raise ValueError(f"No se encontró ninguna clase de modelo en el archivo: {model_file_path}")
            
            if len(candidate_classes) == 1:
                model_class = candidate_classes[0]
            else:
                for cls in candidate_classes:
                    if "CNN" in cls.__name__ or "Model" in cls.__name__:
                        model_class = cls
                        break
                if model_class is None:
                    raise ValueError(f"Múltiples clases encontradas en {model_file_path}. No se pudo identificar la clase del modelo.")

            bot_name = f"CNN_Bot_with_{os.path.basename(model_file_path).replace('.py', '')}_weights_{os.path.basename(weights_file_path).replace('.pt', '')}"
            temp_bot_instance = bot_class(name=bot_name, model_class=model_class, model_path=weights_file_path)
            
            bot_config = {
                'bot_name': bot_name,
                'bot_class': bot_class,
                'model_class': model_class,
                'model_path': model_file_path,
                'weights_path': weights_file_path
            }
            
            return True, f"Configuración de CNN Bot con modelo '{os.path.basename(model_file_path)}' y pesos '{os.path.basename(weights_file_path)}' parece ser válida.", bot_config

        except Exception as e:
            return False, f"Error al validar el modelo, pesos o el bot: {e}", None
        finally:
            # Remove the added path from sys.path
            if temp_sys_path_added and quartopy_root in sys.path:
                sys.path.remove(quartopy_root)

    def _open_model_file_dialog(self):
        self.save_btn.setEnabled(False) # Disable save button on file change
        initial_dir = os.path.join(os.getcwd(), 'quartopy', 'models')
        selected_file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo de Modelo para CNN Bot", initial_dir, "Python Files (*.py);;All Files (*)")
        if selected_file_path:
            quartopy_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            destination_dir = os.path.join(quartopy_root, 'quartopy', 'models')
            os.makedirs(destination_dir, exist_ok=True)
            
            final_model_file_path = None
            # Check if the file is already in the destination folder
            if not os.path.abspath(selected_file_path).startswith(os.path.abspath(destination_dir)):
                try:
                    dest_file_path = os.path.join(destination_dir, os.path.basename(selected_file_path))
                    shutil.copy2(selected_file_path, dest_file_path)
                    final_model_file_path = dest_file_path
                    QMessageBox.information(self, "Archivo Copiado", f"El archivo '{os.path.basename(selected_file_path)}' ha sido copiado a '{os.path.relpath(destination_dir, quartopy_root)}'.")
                except Exception as e:
                    QMessageBox.critical(self, "Error de Copia", f"No se pudo copiar el archivo: {e}")
                    self.model_file_path = None
            else:
                final_model_file_path = selected_file_path
            
            self.model_file_path = final_model_file_path

            # --- Lógica para modificar el archivo copiado ---
            if self.model_file_path:
                try:
                    with open(self.model_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    old_import = "from models.NN_abstract import NN_abstract"
                    new_import = "from quartopy.models.NN_abstract import NN_abstract"

                    if old_import in content:
                        modified_content = content.replace(old_import, new_import)
                        with open(self.model_file_path, 'w', encoding='utf-8') as f:
                            f.write(modified_content)
                        QMessageBox.information(self, "Import Corregido", "La importación de 'NN_abstract' ha sido corregida en el archivo del modelo.")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Error al Modificar Archivo", f"No se pudo modificar la importación en el archivo del modelo: {e}")
                    self.model_file_path = None # Invalidar selección si falla la modificación
            # --- Fin de la lógica de modificación ---

            self.model_path_label.setText(os.path.basename(self.model_file_path) if self.model_file_path else "No se ha seleccionado archivo")
        else:
            self.model_file_path = None
            self.model_path_label.setText("No se ha seleccionado archivo")
        self._update_verify_button_state()

    def _open_weights_file_dialog(self):
        self.save_btn.setEnabled(False) # Disable save button on file change
        initial_dir = os.path.join(os.getcwd(), 'quartopy', 'CHECKPOINTS')
        selected_file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo de Pesos para CNN Bot", initial_dir, "PyTorch Models (*.pt);;All Files (*)")
        if selected_file_path:
            quartopy_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            destination_dir = os.path.join(quartopy_root, 'quartopy', 'CHECKPOINTS')
            os.makedirs(destination_dir, exist_ok=True)
            
            # Check if the file is already in the destination folder
            if not os.path.abspath(selected_file_path).startswith(os.path.abspath(destination_dir)):
                try:
                    dest_file_path = os.path.join(destination_dir, os.path.basename(selected_file_path))
                    shutil.copy2(selected_file_path, dest_file_path)
                    self.weights_file_path = dest_file_path
                    QMessageBox.information(self, "Archivo Copiado", f"El archivo '{os.path.basename(selected_file_path)}' ha sido copiado a '{os.path.relpath(destination_dir, quartopy_root)}'.")
                except Exception as e:
                    QMessageBox.critical(self, "Error de Copia", f"No se pudo copiar el archivo: {e}")
                    self.weights_file_path = None
            else:
                self.weights_file_path = selected_file_path
            
            self.weights_path_label.setText(os.path.basename(self.weights_file_path) if self.weights_file_path else "No se ha seleccionado archivo")
        else:
            self.weights_file_path = None
            self.weights_path_label.setText("No se ha seleccionado archivo")
        self._update_verify_button_state()

    def _update_verify_button_state(self):
        self.verify_btn.setEnabled(self.model_file_path is not None and self.weights_file_path is not None)

    def _verify_bot_config(self):
        """Verifica la configuración del bot sin guardarla."""
        is_valid, message, _ = self._perform_bot_validation(self.model_file_path, self.weights_file_path)
        if is_valid:
            QMessageBox.information(self, "Verificación Exitosa", message)
            self.save_btn.setEnabled(True) # Enable save button on successful verification
        else:
            QMessageBox.warning(self, "Error de Verificación", message)
            self.save_btn.setEnabled(False) # Ensure it's disabled on failure

    def _save_bot_config(self):
        """Guarda la configuración del bot si es válida."""
        is_valid, message, bot_config = self._perform_bot_validation(self.model_file_path, self.weights_file_path)
        if is_valid:
            self.bot_added_successfully.emit(bot_config)
            QMessageBox.information(self, "Éxito", f"Bot '{bot_config['bot_name']}' cargado exitosamente.")
            self.accept() # Close dialog on success
        else:
            QMessageBox.critical(self, "Error al Guardar Bot", message)