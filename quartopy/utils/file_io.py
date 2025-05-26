import csv
import os
from datetime import datetime
from colorama import Fore, Style


def export_history_to_csv(self, match_number=None):
    """Exporta el historial a un CSV con nombre que incluye match, fecha y hora"""
    # Crear directorio si no existe
    if not os.path.exists("partidas_guardadas"):
        os.makedirs("partidas_guardadas")

    # Generar nombre de archivo con formato: MatchX_YYYY-MM-DD_HH-MM-SS.csv
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if match_number is not None:
        filename = f"Match{match_number}_{current_time}.csv"
    else:
        filename = f"Partida_{current_time}.csv"

    filepath = os.path.join("partidas_guardadas", filename)

    with open(filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Escribir metadatos al inicio del archivo
        writer.writerow(["Juego: Quarto"])
        writer.writerow(
            [f"Partida: {match_number}" if match_number else "Partida única"]
        )
        writer.writerow([f"Fecha: {current_time.replace('_', ' ')}"])
        writer.writerow([f"Jugador 1: {self.player1.name}"])
        writer.writerow([f"Jugador 2: {self.player2.name}"])
        writer.writerow(
            [f"Resultado: {self.winner_name if self.winner_name else 'Sin determinar'}"]
        )
        writer.writerow(
            [f"Posición: {self.player_turn if self.winner_name else 'Sin determinar'}"]
        )
        writer.writerow([])  # Línea vacía

        # Escribir cabecera de movimientos
        writer.writerow(["Movimiento", "Jugador", "Acción", "Pieza", "Posición"])

        # Escribir movimientos
        for i, move in enumerate(self.move_history, start=1):
            writer.writerow(
                [
                    i,
                    move["player"],
                    move["action"],
                    move["piece"],
                    (
                        f"({move['position'][0]}, {move['position'][1]})"
                        if move["position"]
                        else "N/A"
                    ),
                ]
            )

    print(f"\n{Fore.GREEN}Historial guardado en: {filepath}{Style.RESET_ALL}")
    return filepath
