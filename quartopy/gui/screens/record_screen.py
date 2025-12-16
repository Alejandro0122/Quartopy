# quartopy/gui/screens/record_screen.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt5.QtGui import QFont, QColor, QBrush
from PyQt5.QtCore import Qt, pyqtSignal

class RecordScreen(QWidget):
    """Pantalla para mostrar los records de puntuación"""
    
    # Señal para volver al menú
    back_to_menu = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setStyleSheet("background-color: #1a1a1a; color: white;")
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 30, 50, 30)
        
        # Título
        title_label = QLabel("RÉCORDS DE PUNTUACIÓN")
        title_label.setFont(QFont("Arial", 28, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #FFD700; 
            padding: 15px;
        """)
        layout.addWidget(title_label)
        
        # Tabla de records
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["JUGADOR", "INTENTOS"])
        self.table.setRowCount(10)  # 10 filas fijas
        
        # Configurar encabezados
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #333333;
                color: #FFD700;
                font-weight: bold;
                font-size: 16px;
                padding: 15px;
                border: none;
                border-bottom: 2px solid #FFD700;
            }
        """)
        
        # Ocultar encabezado vertical
        self.table.verticalHeader().setVisible(False)
        
        # Estilo de la tabla
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a2a;
                border: 2px solid #FFD700;
                border-radius: 8px;
                gridline-color: #555555;
                font-size: 14px;
                selection-background-color: #FFD700;
                selection-color: black;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #444444;
                text-align: center;
            }
        """)
        
        # Configurar tabla como no editable
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # Llenar la tabla con datos de ejemplo (o vacíos)
        self.initialize_table()
        
        layout.addWidget(self.table)
        
        # Botón Volver
        buttons_layout = QHBoxLayout()
        self.back_btn = QPushButton("Volver al Menú")
        self.back_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.back_btn.setFixedSize(200, 50)
        self.back_btn.setStyleSheet("""
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
        """)
        self.back_btn.clicked.connect(self.go_back)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.back_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def initialize_table(self):
        """Inicializa la tabla con datos de ejemplo"""
        # Datos de ejemplo
        records = [
            {"player": "Carlos", "attempts": 8},
            {"player": "Ana", "attempts": 6},
            {"player": "Luis", "attempts": 12},
            {"player": "María", "attempts": 9},
            {"player": "Pedro", "attempts": 7},
            {"player": "Sofía", "attempts": 10},
            {"player": "", "attempts": ""},
            {"player": "", "attempts": ""},
            {"player": "", "attempts": ""},
            {"player": "", "attempts": ""},
        ]
        
        for i in range(10):
            # Columna JUGADOR
            player_item = QTableWidgetItem(records[i]["player"] if i < len(records) else "")
            player_item.setTextAlignment(Qt.AlignCenter)
            player_item.setFont(QFont("Arial", 12))
            
            # Columna INTENTOS
            attempts_text = str(records[i]["attempts"]) if i < len(records) and records[i]["attempts"] != "" else ""
            attempts_item = QTableWidgetItem(attempts_text)
            attempts_item.setTextAlignment(Qt.AlignCenter)
            attempts_item.setFont(QFont("Arial", 12, QFont.Bold))
            
            # Colorear las primeras filas con datos
            if i < len(records) and records[i]["player"]:
                if i == 0:  # Primer lugar - Oro
                    player_item.setForeground(QBrush(QColor("#FFD700")))
                    attempts_item.setForeground(QBrush(QColor("#FFD700")))
                elif i == 1:  # Segundo lugar - Plata
                    player_item.setForeground(QBrush(QColor("#C0C0C0")))
                    attempts_item.setForeground(QBrush(QColor("#C0C0C0")))
                elif i == 2:  # Tercer lugar - Bronce
                    player_item.setForeground(QBrush(QColor("#CD7F32")))
                    attempts_item.setForeground(QBrush(QColor("#CD7F32")))
                else:  # Resto
                    player_item.setForeground(QBrush(QColor("#FFFFFF")))
                    attempts_item.setForeground(QBrush(QColor("#FFFFFF")))
            
            self.table.setItem(i, 0, player_item)
            self.table.setItem(i, 1, attempts_item)
    
    def set_records(self, records_data):
        """Establece los datos de la tabla desde fuera"""
        for i in range(min(10, len(records_data))):
            record = records_data[i]
            
            # Columna JUGADOR
            player_item = QTableWidgetItem(record.get("player", ""))
            player_item.setTextAlignment(Qt.AlignCenter)
            player_item.setFont(QFont("Arial", 12))
            
            # Columna INTENTOS
            attempts_item = QTableWidgetItem(str(record.get("attempts", "")))
            attempts_item.setTextAlignment(Qt.AlignCenter)
            attempts_item.setFont(QFont("Arial", 12, QFont.Bold))
            
            # Colorear según la posición
            if i == 0:  # Primer lugar - Oro
                player_item.setForeground(QBrush(QColor("#FFD700")))
                attempts_item.setForeground(QBrush(QColor("#FFD700")))
            elif i == 1:  # Segundo lugar - Plata
                player_item.setForeground(QBrush(QColor("#C0C0C0")))
                attempts_item.setForeground(QBrush(QColor("#C0C0C0")))
            elif i == 2:  # Tercer lugar - Bronce
                player_item.setForeground(QBrush(QColor("#CD7F32")))
                attempts_item.setForeground(QBrush(QColor("#CD7F32")))
            else:  # Resto
                player_item.setForeground(QBrush(QColor("#FFFFFF")))
                attempts_item.setForeground(QBrush(QColor("#FFFFFF")))
            
            self.table.setItem(i, 0, player_item)
            self.table.setItem(i, 1, attempts_item)
        
        # Limpiar las filas restantes si hay menos de 10 records
        for i in range(len(records_data), 10):
            self.table.setItem(i, 0, QTableWidgetItem(""))
            self.table.setItem(i, 1, QTableWidgetItem(""))
    
    def go_back(self):
        """Vuelve al menú principal"""
        self.back_to_menu.emit()
    
    def showEvent(self, event):
        """Se ejecuta cuando se muestra la pantalla"""
        super().showEvent(event)
        # Puedes cargar datos reales aquí si los tienes


# Función de prueba
def test_record_screen():
    """Función de prueba para la pantalla de records"""
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    def on_back_to_menu():
        print("Volviendo al menú principal")
        app.quit()
    
    # Crear pantalla
    screen = RecordScreen()
    screen.back_to_menu.connect(on_back_to_menu)
    
    # Ejemplo: establecer datos desde fuera
    records_data = [
        {"player": "Carlos", "attempts": 12},
        {"player": "Ana", "attempts": 8},
        {"player": "Luis", "attempts": 15},
        {"player": "María", "attempts": 10},
        {"player": "Pedro", "attempts": 6},
    ]
    screen.set_records(records_data)
    
    screen.setWindowTitle("Quarto - Records de Puntuación")
    screen.resize(800, 600)
    screen.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    test_record_screen()