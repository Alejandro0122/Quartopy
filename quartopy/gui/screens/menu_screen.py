import sys
import random
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QRadialGradient
from .rules_screen import RulesScreen # Importar RulesScreen

# --- CLASE PARA PARTÍCULAS TIPO "ESTELA" ---
class Particle:
    def __init__(self, max_width, max_height):
        self.max_w = max_width
        self.max_h = max_height
        
        # Nacimiento: Esquina superior derecha
        offset = random.uniform(-100, 100)
        self.position = QPointF(max_width + 50, -50 + offset)
        
        # Velocidad diagonal arrastrada
        self.vx = random.uniform(-4.0, -7.0)
        self.vy = random.uniform(3.0, 5.0)
        
        self.size = random.uniform(5, 15)
        self.color = QColor(255, 215, 0, random.randint(100, 200)) # Dorado
        self.lifespan = 300
        self.age = 0

    def update(self):
        self.position.setX(self.position.x() + self.vx)
        self.position.setY(self.position.y() + self.vy)
        self.age += 1
        
        if self.age > 200:
            alpha = self.color.alpha()
            if alpha > 2: self.color.setAlpha(alpha - 2)

    def is_dead(self):
        return self.age >= self.lifespan or self.position.x() < -100 or self.position.y() > self.max_h + 100

# --- CLASE MENU PRINCIPAL ACTUALIZADA ---
class MenuScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Menú Principal")
        self.resize(1000, 700) # Tamaño coherente con el estilo anterior

        # Fondo azul profundo del código original
        self.background_color = QColor("#0C0E1D")

        # --- SISTEMA DE PARTÍCULAS ---
        self.particles = []
        self.particle_timer = QTimer(self)
        self.particle_timer.timeout.connect(self.update_particles)
        # No iniciar el timer aquí, se iniciará en showEvent

        # --- TÍTULO ---
        self.title_label = QLabel("Menú Principal", self)
        self.title_label.setFont(QFont("Georgia", 40, QFont.Bold)) # Estilo elegante
        self.title_label.setStyleSheet("color : #FFD700; background: transparent;")
        self.title_label.setAlignment(Qt.AlignCenter)

        # --- ESTILO DE BOTONES (Mantenido y Refinado) ---
        btn_style = """
            QPushButton {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                border: 2px solid white;
                padding: 15px;
                font-size: 14pt;
                border-radius: 10px;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
                border: 2px solid #FFD700;
            }
        """

        # Botones
        self.btn_play = QPushButton('Jugar', self)
        self.btn_play.setStyleSheet(btn_style)

        self.btn_record = QPushButton('Tabla de puntajes', self)
        self.btn_record.setStyleSheet(btn_style)

        self.btn_rules = QPushButton('Reglas del Juego', self)
        self.btn_rules.setStyleSheet(btn_style)

        self.btn_exit = QPushButton('Salir', self)
        self.btn_exit.setStyleSheet(btn_style)

        # Layout
        layout = QVBoxLayout(self)
        layout.addStretch(1)
        layout.addWidget(self.title_label, 0, Qt.AlignCenter)
        layout.addSpacing(40)
        layout.addWidget(self.btn_play, 0, Qt.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(self.btn_record, 0, Qt.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(self.btn_rules, 0, Qt.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(self.btn_exit, 0, Qt.AlignCenter)
        layout.addStretch(1)

        # Inicializar la pantalla de reglas (se creará una vez y se reutilizará)
        # Esta instancia es manejada por MainWindow, no por MenuScreen directamente.
        # self.rules_screen = RulesScreen(self)
        # self.rules_screen.hide() # Ocultarla inicialmente

    def update_particles(self):
        if len(self.particles) < 60:
            self.particles.append(Particle(self.width(), self.height()))

        for particle in list(self.particles):
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)
        self.update() # Llama al paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 1. Dibujar el fondo azul sólido
        painter.fillRect(self.rect(), self.background_color)

        # 2. Dibujar las partículas doradas
        for p in self.particles:
            gradient = QRadialGradient(p.position, p.size)
            gradient.setColorAt(0, p.color)
            gradient.setColorAt(1, QColor(255, 215, 0, 0)) # Desvanecimiento
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(p.position, p.size, p.size)
        
        super().paintEvent(event)

    def showEvent(self, event):
        """Se llama cuando el widget se muestra."""
        super().showEvent(event)
        if not self.particle_timer.isActive():
            self.particle_timer.start(20)
        self.update() # Asegurar un redibujado al mostrarse

    def hideEvent(self, event):
        """Se llama cuando el widget se oculta."""
        super().hideEvent(event)
        if self.particle_timer.isActive():
            self.particle_timer.stop()
    
    # El método show_rules_screen ya no es necesario aquí, ya que la conexión se hace en MainWindow
    # def show_rules_screen(self):
    #     self.hide() # Oculta la pantalla del menú
    #     self.rules_screen.show() # Muestra la pantalla de reglas

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MenuScreen()
    window.show()
    sys.exit(app.exec_())