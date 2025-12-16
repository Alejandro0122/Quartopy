import sys
from PyQt5.QtWidgets import QApplication
from .gui.main_window import MainWindow 

def main():
    # 1. Crea la instancia de QApplication
    app = QApplication(sys.argv)
    
    # 2. Crea una instancia de la ventana principal/gestor
    # Ya no usamos StartScreen directamente, sino MainWindow.
    window = MainWindow() 
    
    # 3. Muestra la ventana
    window.show()
    
    # 4. Inicia el bucle de eventos de la aplicación
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()