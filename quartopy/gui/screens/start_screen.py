import sys
import random
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QGraphicsColorizeEffect, QApplication
from PyQt5.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QRadialGradient

# --- CLASE PARA PARTÍCULAS TIPO "ESTELA" ---
class Particle:
    def __init__(self, max_width, max_height):
        self.max_w = max_width
        self.max_h = max_height
        
        # Nacimiento: En una franja estrecha cerca de la esquina superior derecha
        offset = random.uniform(-100, 100)
        self.position = QPointF(max_width + 50, -50 + offset)
        
        # Velocidad: Movimiento "arrastrado" (más rápido en X que en Y para que crucen)
        self.vx = random.uniform(-4.0, -7.0)
        self.vy = random.uniform(3.0, 5.0)
        
        self.size = random.uniform(5, 15)
        self.color = QColor(255, 215, 0, random.randint(100, 200))
        self.lifespan = 300  # Vida larga para que lleguen al otro lado
        self.age = 0

    def update(self):
        # Efecto de arrastre
        self.position.setX(self.position.x() + self.vx)
        self.position.setY(self.position.y() + self.vy)
        self.age += 1
        
        # Desvanecimiento al final de su vida
        if self.age > 200:
            alpha = self.color.alpha()
            if alpha > 2: self.color.setAlpha(alpha - 2)

    def is_dead(self):
        return self.age >= self.lifespan or self.position.x() < -100 or self.position.y() > self.max_h + 100

# --- CLASE PRINCIPAL ---
class StartScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Quarto - Inicio')
        self.resize(1000, 700)
        
        self.background_color = QColor("#0C0E1D")

        # --- TÍTULO ANIMADO (Blanco <-> Amarillo lento) ---
        self.full_text = "QUARTO"
        self.current_text = ""
        
        self.title_label = QLabel("", self)
        self.title_label.setFont(QFont("Georgia", 110, QFont.Bold))
        self.title_label.setStyleSheet("color: white; background: transparent;")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.glow_effect = QGraphicsColorizeEffect(self)
        self.glow_effect.setColor(QColor(255, 255, 0))
        self.title_label.setGraphicsEffect(self.glow_effect)

        # Animación de resplandor
        self.glow_anim = QPropertyAnimation(self.glow_effect, b"strength")
        self.glow_anim.setDuration(4000)
        self.glow_anim.setStartValue(0.0)
        self.glow_anim.setEndValue(1.0)  
        self.glow_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.glow_anim.setLoopCount(-1)
        self.glow_anim.start()

        self.typewriter_timer = QTimer(self)
        self.typewriter_timer.timeout.connect(self.update_text)
        self.char_index = 0
        self.typewriter_timer.start(180)

        # --- INTERFAZ ---
        self.subtitle_label = QLabel("DESAFÍA TU MENTE", self)
        self.subtitle_label.setStyleSheet("font-size: 16pt; color: rgba(255, 255, 255, 120); letter-spacing: 10px;")
        self.subtitle_label.setAlignment(Qt.AlignCenter)

        self.btn_style = """
            QPushButton {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                border: 2px solid white;
                padding: 15px;
                font-size: 14pt;
                border-radius: 10px;
                min-width: 280px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
            }
        """

        self.start_button = QPushButton('Comenzar a Jugar', self)
        self.start_button.setStyleSheet(self.btn_style)
        self.exit_button = QPushButton('Salir', self)
        self.exit_button.setStyleSheet(self.btn_style)

        layout = QVBoxLayout(self)
        layout.addStretch(2)
        layout.addWidget(self.title_label, 0, Qt.AlignCenter)
        layout.addWidget(self.subtitle_label, 0, Qt.AlignCenter)
        layout.addSpacing(60)
        layout.addWidget(self.start_button, 0, Qt.AlignCenter)
        layout.addWidget(self.exit_button, 0, Qt.AlignCenter)
        layout.addStretch(1)

        # --- SISTEMA DE PARTÍCULAS ---
        self.particles = []
        self.particle_timer = QTimer(self)
        self.particle_timer.timeout.connect(self.update_particles)
        self.particle_timer.start(20)

    def update_text(self):
        if self.char_index < len(self.full_text):
            self.current_text += self.full_text[self.char_index]
            self.title_label.setText(self.current_text)
            self.char_index += 1

    def update_particles(self):
        if len(self.particles) < 60:
            self.particles.append(Particle(self.width(), self.height()))

        for particle in list(self.particles):
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fondo sólido azul profundo
        painter.fillRect(self.rect(), self.background_color)

        # Dibujar partículas con brillo radial
        for p in self.particles:
            gradient = QRadialGradient(p.position, p.size)
            gradient.setColorAt(0, p.color)
            gradient.setColorAt(1, QColor(255, 215, 0, 0))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(p.position, p.size, p.size)
        
        super().paintEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StartScreen()
    window.show()
    sys.exit(app.exec_())