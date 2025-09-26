# Quartopy - Quarto Game Library

El juego de mesa Quarto implementado en Python con soporte para bots personalizados y partidas automatizadas.

## Descripción

Quarto es un juego de estrategia para dos jugadores que se juega en un tablero de 4x4. El objetivo es formar una línea de cuatro piezas que compartan al menos una característica común (tamaño, color, forma o agujero). Esta implementación incluye soporte para modo 2x2 donde también se puede ganar formando un cuadrado de 2x2 con piezas que compartan características.

## Instalación

Debe instalarse como *package* Python, para ello se debe ejecutar el siguiente comando en la terminal:

```bash
pip install .
```

* En caso de querer instalarlo en modo editable, se debe ejecutar el siguiente comando en la terminal:
```bash
pip install -e .
```

## Uso

### Consola (CLI)

Interfaz de línea de comandos con las siguientes opciones:

```bash
python quarto_CLI.py --player1 random_bot --player2 human --verbose --matches 2 --delay 0
```

**Parámetros disponibles:**
- `--matches`: Número de partidas a jugar (default: 1)
- `--player1`: Jugador #1 (opciones: `random_bot`, `human`)
- `--player2`: Jugador #2 (opciones: `random_bot`, `human`)  
- `--delay`: Retardo en segundos entre movimientos (default: 1.0)
- `--verbose`: Flag para mostrar detalles visuales del juego
- `--folder_bots`: Directorio de los bots (default: "bot/")

### Programático

También puedes usar las funciones principales directamente en tu código:

```python
from quartopy import go_quarto, play_games

# Opción 1: Usar go_quarto para cargar bots desde archivos
matches_data, win_rate = go_quarto(
    matches=10,
    player1_file="random_bot",
    player2_file="human",
    delay=0.5,
    verbose=True,
    builtin_bots=True
)

# Opción 2: Usar play_games con instancias de bots ya creadas
from quartopy.models import BotAI
from bot.random_bot import Quarto_bot as RandomBot

player1 = RandomBot()
player2 = RandomBot()

matches_data, win_rate = play_games(
    matches=100,
    player1=player1,
    player2=player2,
    verbose=False,
    save_match=True,
    mode_2x2=True
)
```

## API Principal

### Función [`go_quarto`](quartopy/game/play.py)

```python
def go_quarto(
    matches: int,
    player1_file: str,
    player2_file: str,
    delay: float = 0,
    params_p1: dict = {},
    params_p2: dict = {},
    verbose: bool = True,
    folder_bots: str = "bot/",
    builtin_bots: bool = False,
    mode_2x2: bool = True,
) -> tuple[list[dict], dict[str, int]]
```

**Descripción**: Inicia un torneo de Quarto entre dos bots cargados desde archivos Python.

**Parámetros**:
- `matches` (int): Número de partidas a jugar en el torneo
- `player1_file` (str): Nombre del script del bot jugador 1 (sin extensión .py). Debe contener una clase `Quarto_bot`
- `player2_file` (str): Nombre del script del bot jugador 2 (sin extensión .py). Debe contener una clase `Quarto_bot`
- `delay` (float, opcional): Retardo entre movimientos en segundos. Por defecto 0
- `params_p1` (dict, opcional): Parámetros adicionales para inicializar el bot jugador 1
- `params_p2` (dict, opcional): Parámetros adicionales para inicializar el bot jugador 2
- `verbose` (bool, opcional): Si True, muestra salida detallada de las partidas. Por defecto True
- `folder_bots` (str, opcional): Directorio donde se encuentran los scripts de los bots. Por defecto "bot/"
- `builtin_bots` (bool, opcional): Si True, usa bots integrados del paquete en lugar de scripts externos. Por defecto False
- `mode_2x2` (bool, opcional): Si True, activa el modo de victoria en cuadrados 2x2. Por defecto True

**Retorna**:
- `tuple`: Una tupla con dos elementos:
  - `matches_data` (list[dict]): Lista de diccionarios con los resultados detallados de cada partida
  - `win_rate` (dict[str, int]): Diccionario con el conteo de victorias por jugador y empates

**Ejemplo**:
```python
matches_data, win_rate = go_quarto(
    matches=50,
    player1_file="my_smart_bot",
    player2_file="random_bot",
    delay=0.1,
    verbose=False,
    builtin_bots=True,
    mode_2x2=True
)
print(f"Resultados: {win_rate}")
# Salida: {'Player 1': 25, 'Player 2': 20, 'Tie': 5}
```

### Función [`play_games`](quartopy/game/play.py)

```python
def play_games(
    matches: int,
    player1: BotAI,
    player2: BotAI,
    delay: float = 0,
    verbose: bool = True,
    PROGRESS_MESSAGE: str = "Playing matches...",
    save_match: bool = True,
    mode_2x2: bool = True,
) -> tuple[list[dict], dict[str, int]]
```

**Descripción**: Ejecuta un torneo de Quarto entre dos jugadores ya instanciados. Esta función ofrece más control sobre la configuración del juego.

**Parámetros**:
- `matches` (int): Número total de partidas a jugar en el torneo
- `player1` ([`BotAI`](quartopy/models/Bot.py)): Instancia del bot jugador 1 que implementa la interfaz BotAI
- `player2` ([`BotAI`](quartopy/models/Bot.py)): Instancia del bot jugador 2 que implementa la interfaz BotAI
- `delay` (float, opcional): Tiempo de espera en segundos entre cada movimiento. Por defecto 0
- `verbose` (bool, opcional): Si True, muestra el progreso visual del juego en consola. Por defecto True
- `PROGRESS_MESSAGE` (str, opcional): Mensaje personalizado para la barra de progreso. Por defecto "Playing matches..."
- `save_match` (bool, opcional): Si True, guarda el historial de cada partida en formato CSV. Por defecto True
- `mode_2x2` (bool, opcional): Si True, activa el modo de victoria en cuadrados 2x2 además de las líneas tradicionales. Por defecto True

**Retorna**:
- `tuple`: Una tupla con dos elementos:
  - `matches_data` (list[dict[str, Any]]): Lista donde cada elemento es un diccionario con:
    - `move_history`: Historial completo de movimientos de la partida
    - `Player 1`: Nombre del jugador 1
    - `Player 2`: Nombre del jugador 2  
    - `result`: Resultado de la partida ("Player 1", "Player 2", o "Tie")
  - `win_rate` (dict[str, int]): Diccionario con estadísticas del torneo:
    - Claves: "Player 1", "Player 2", "Tie"
    - Valores: Número de partidas ganadas por cada resultado

**Ejemplo**:
```python
from bot.random_bot import Quarto_bot as RandomBot
from bot.human import Quarto_bot as HumanBot

bot1 = RandomBot()
bot2 = HumanBot()

matches_data, stats = play_games(
    matches=10,
    player1=bot1,
    player2=bot2,
    delay=1.0,
    verbose=True,
    save_match=True,
    mode_2x2=True
)

# Analizar resultados
for i, match in enumerate(matches_data):
    print(f"Partida {i+1}: Ganador = {match['result']}")
    
print(f"\nEstadísticas finales: {stats}")
```

## Estructura del Proyecto

```
quartopy/
├── __init__.py                 # Exportaciones principales
├── game/
│   ├── board.py               # Lógica del tablero
│   ├── piece.py               # Definición de piezas
│   ├── play.py                # Funciones principales de juego
│   └── quarto_game.py         # Clase principal del juego
├── models/
│   ├── Bot.py                 # Interfaz abstracta para bots
│   └── __init__.py            # Utilidades de carga de bots
└── utils/
    ├── logger.py              # Sistema de logging con colores
    └── __init__.py

bot/                           # Bots de ejemplo (built-in)
├── random_bot.py              # Bot que juega aleatoriamente
└── human.py                   # Interfaz para jugador humano

partidas_guardadas/            # Archivos CSV de partidas
├── 2025-09-26_16-21-42_match001.csv
└── ...

tests/                         # Notebooks de prueba
├── view_match.ipynb           # Tests de funciones de juego
└── view_conversion.ipynb      # Tests de conversiones AI

quarto_CLI.py                  # Interfaz de línea de comandos
play_game.py                   # Script de ejemplo
```

## Creando tu Propio Bot

Para crear un bot personalizado, debes implementar la interfaz [`BotAI`](quartopy/models/Bot.py):

```python
from quartopy import BotAI, Piece, QuartoGame

class Quarto_bot(BotAI):
    @property
    def name(self) -> str:
        return "MiBot"
    
    def __init__(self, **kwargs):
        # Inicialización de tu bot
        pass
    
    def select(self, game: QuartoGame, ith_option: int = 0, *args, **kwargs) -> Piece:
        """Selecciona una pieza para el oponente.
        
        Args:
            game: Instancia actual del juego
            ith_option: Número de intento (para manejo de errores)
            
        Returns:
            Piece: Pieza válida del storage_board
        """
        # Lógica para seleccionar una pieza para el oponente
        # Debe retornar un objeto Piece válido del storage_board
        valid_pieces = game.storage_board.get_valid_pieces()
        # Tu lógica aquí...
        return selected_piece
    
    def place_piece(self, game: QuartoGame, piece: Piece, ith_option: int = 0, *args, **kwargs) -> tuple[int, int]:
        """Coloca la pieza en el tablero.
        
        Args:
            game: Instancia actual del juego
            piece: Pieza a colocar
            ith_option: Número de intento (para manejo de errores)
            
        Returns:
            tuple[int, int]: Coordenadas (fila, columna) donde colocar la pieza
        """
        # Lógica para colocar la pieza en el tablero
        # Debe retornar una tupla (fila, columna) válida
        valid_moves = game.game_board.get_valid_moves()
        # Tu lógica aquí...
        return (row, col)
```

### Bots Incluidos

#### RandomBot ([`bot/random_bot.py`](bot/random_bot.py))
Bot que selecciona piezas y posiciones de manera completamente aleatoria.

#### HumanBot ([`bot/human.py`](bot/human.py))
Interfaz interactiva que permite a un humano jugar mediante input de consola.

## Sistema de Archivos de Partidas

Las partidas se guardan automáticamente en la carpeta [`partidas_guardadas/`](partidas_guardadas/) en formato CSV con el siguiente nombre: `YYYY-MM-DD_HH-MM-SS_matchXXX.csv`

### Contenido de los archivos CSV:
- **Movimiento**: Número secuencial del movimiento
- **Jugador**: Nombre del bot que realizó el movimiento
- **Acción**: "selected" (selección de pieza) o "placed" (colocación de pieza)
- **Pieza**: Descripción completa de la pieza (solo en selección)
- **Pieza Index**: Índice numérico de la pieza (0-15)
- **Posición**: Coordenadas (fila, columna) donde se colocó la pieza
- **Posición Index**: Índice lineal de la posición (0-15)
- **Intento**: Número de intentos requeridos para el movimiento válido
- **Tablero**: Estado serializado del tablero después del movimiento

### Ejemplo de entrada CSV:
```csv
Movimiento,Jugador,Acción,Pieza,Pieza Index,Posición,Posición Index,Intento,Tablero
1,Human_bot,selected,"LITTLE, BLACK, CIRCLE, WITHOUT_HOLE",0,N/A,N/A,1,N/A
2,RandomBot,placed,N/A,N/A,"(0, 1)",1,1,010000...
```

## Características del Juego

### Modos de Victoria
- **Modo Clásico**: Victoria por líneas horizontales, verticales o diagonales
- **Modo 2x2**: Victoria adicional por cuadrados de 2x2 (configurable con `mode_2x2=True`)

### Características de las Piezas
Cada pieza tiene 4 atributos binarios:
- **Tamaño**: LITTLE (pequeña) / TALL (alta)
- **Color**: BLACK (negro) / WHITE (blanco)  
- **Forma**: CIRCLE (círculo) / SQUARE (cuadrado)
- **Agujero**: WITHOUT (sin agujero) / WITH (con agujero)

### Sistema de Logging
El sistema incluye logging con colores utilizando [`colorama`](quartopy/utils/logger.py) para mejor visualización en consola.

## Dependencias

Ver [requirements.txt](requirements.txt) para la lista completa de dependencias:

```txt
click==8.3.0          # Para la interfaz de línea de comandos
colorama==0.4.6       # Para output coloreado en consola  
numpy==2.3.3          # Para operaciones matriciales y vectoriales
tqdm==4.67.1          # Para barras de progreso
```

## Ejemplos de Uso

### Ejemplo básico con script
Ver [`play_game.py`](play_game.py) para un ejemplo simple:

```python
from quartopy import go_quarto

results = go_quarto(
    matches=2,
    player1_file="human",
    player2_file="random_bot",
    delay=0,
    verbose=True,
)
```

### Análisis de partidas
Los datos de las partidas pueden ser analizados programáticamente:

```python
matches_data, win_rate = go_quarto(
    matches=100,
    player1_file="random_bot",
    player2_file="random_bot",
    verbose=False,
    save_match=True
)

# Estadísticas generales
print(f"Total de partidas: {sum(win_rate.values())}")
print(f"Victorias Player 1: {win_rate.get('Player 1', 0)}")
print(f"Victorias Player 2: {win_rate.get('Player 2', 0)}")
print(f"Empates: {win_rate.get('Tie', 0)}")

# Análisis de movimientos por partida
for i, match in enumerate(matches_data):
    print(f"Partida {i+1}: {len(match['move_history'])} movimientos")
```

## Notas de Desarrollo

- Requiere Python ≥ 3.10
- Compatible con sistemas Windows, Linux y macOS
- El sistema de manejo de errores permite hasta 16 intentos por movimiento
- Los bots integrados se cargan automáticamente desde la carpeta [`bot/`](bot/)