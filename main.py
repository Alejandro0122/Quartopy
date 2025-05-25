import click
import time
import os


from quartopy import QuartoGame
from colorama import Fore, Back, Style
import os


@click.command()
@click.option("--matches", default=1, help="Número de partidas a jugar", type=int)
@click.option(
    "--player1",
    default="ai1",
    type=click.Choice(["ai1", "ai2"], case_sensitive=False),
    help="Tipo de jugador 1 (ai1 o ai2)",
)
@click.option(
    "--player2",
    default="ai2",
    type=click.Choice(["ai1", "ai2"], case_sensitive=False),
    help="Tipo de jugador 2 (ai1 o ai2)",
)
@click.option(
    "--delay", default=1.0, help="Retardo entre movimientos en segundos", type=float
)
@click.option("--verbose", is_flag=True, help="Mostrar salida detallada")
def play_quarto(matches, player1, player2, delay, verbose):
    """Juego Quarto con jugadores configurables."""

    print(
        f"\n{Back.BLUE}{Fore.WHITE}{' INICIANDO TORNEO DE QUARTO ':=^60}{Style.RESET_ALL}"
    )
    print(f" Partidas: {matches}")
    print(f" Jugador 1: {player1.upper()}")
    print(f" Jugador 2: {player2.upper()}")
    print(f" Retardo: {delay} segundos\n")

    # Crear directorio para guardar partidas si no existe
    if not os.path.exists("partidas_guardadas"):
        os.makedirs("partidas_guardadas")

    results = {f"{player1.upper()} (P1)": 0, f"{player2.upper()} (P2)": 0, "Empates": 0}

    for match in range(1, matches + 1):
        print(
            f"\n{Back.MAGENTA}{Fore.WHITE}{f' PARTIDA {match}/{matches} ':=^60}{Style.RESET_ALL}"
        )

        game = QuartoGame(player1_type=player1, player2_type=player2)

        try:
            while not game.winner_name and not game.game_board.is_full():
                if verbose:
                    game.display_boards()
                game.play_ai_turn()

                if delay > 0:
                    time.sleep(delay)

            # Mostrar resultado de la partida
            if game.winner_name:
                winner = game.winner_name
                if "Player 1" in winner:
                    results[f"{player1.upper()} (P1)"] += 1
                else:
                    results[f"{player2.upper()} (P2)"] += 1

                print(
                    f"\n{Back.GREEN}{Fore.WHITE} RESULTADO: {winner.upper()} GANA {Style.RESET_ALL}"
                )
            else:
                results["Empates"] += 1
                print(
                    f"\n{Back.YELLOW}{Fore.BLACK} RESULTADO: EMPATE {Style.RESET_ALL}"
                )

            # Exportar historial con número de match
            saved_file = game.export_history_to_csv(match_number=match)
            print(f" Partida guardada como: {os.path.basename(saved_file)}")

            if match < matches:
                print(f"\n{Fore.CYAN}Preparando siguiente partida...{Style.RESET_ALL}")
                time.sleep(2)

        except Exception as e:
            print(f"{Back.RED}Error en la partida {match}: {str(e)}{Style.RESET_ALL}")
            continue

    # Resumen final
    print(f"\n{Back.BLUE}{Fore.WHITE}{' RESULTADOS FINALES ':=^60}{Style.RESET_ALL}")
    print(f" Partidas totales: {matches}")
    print("-" * 60)
    for player, wins in results.items():
        print(f" {player:<15}: {wins} victorias")
    print("-" * 60)
    print(f" Todas las partidas guardadas en: {os.path.abspath('partidas_guardadas')}")
    print(f"{Back.BLUE}{Fore.WHITE}{'='*60}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    play_quarto()
