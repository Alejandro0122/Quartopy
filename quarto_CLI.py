from quartopy import QuartoGame, logger
from quartopy.models import load_bot_class

import click
import time
import os
from colorama import Fore, Back, Style
from os import path

logger.debug(f"{__name__} importado correctamente")


@click.command()
@click.option("--matches", default=1, help="Número de partidas a jugar", type=int)
@click.option(
    "--player1",
    default="random_bot",
    type=click.Choice(["random_bot"], case_sensitive=False),
    help="nombre del script del jugador 1 (ej. random_bot)",
)
@click.option(
    "--player2",
    default="random_bot",
    type=click.Choice(["random_bot"], case_sensitive=False),
    help="nombre del script del jugador 2 (ej. random_bot)",
)
@click.option(
    "--delay", default=1.0, help="Retardo entre movimientos en segundos", type=float
)
@click.option("--verbose", is_flag=True, help="Mostrar salida detallada")
@click.option("--folder_bots", help="Directorio de los bots", default="bot/")
def play_quarto(matches, player1, player2, delay, verbose, folder_bots):
    """Juego Quarto con jugadores configurables."""

    print(
        f"\n{Back.BLUE}{Fore.BLACK}{' INICIANDO TORNEO DE QUARTO ':=^60}{Style.RESET_ALL}"
    )
    logger.info(
        f"Iniciando torneo de Quarto con {matches} partidas entre {player1} y {player2}"
    )

    # Cargar clases de los bots
    player1_class = load_bot_class(path.join(folder_bots, f"{player1}.py"))
    player2_class = load_bot_class(path.join(folder_bots, f"{player2}.py"))
    player1 = player1_class()
    player2 = player2_class()

    print(f" Partidas: {matches}")
    print(f" Jugador 1: {player1.name}")
    print(f" Jugador 2: {player2.name}")
    print(f" Retardo: {delay} segundos\n")

    # Crear directorio para guardar partidas si no existe
    if not os.path.exists("partidas_guardadas"):
        os.makedirs("partidas_guardadas")

    results = {f"{player1.name} (P1)": 0, f"{player2.name} (P2)": 0, "Empates": 0}

    for match in range(1, matches + 1):
        print(
            f"\n{Back.BLUE}{Fore.BLACK}{f' PARTIDA {match}/{matches} ':=^60}{Style.RESET_ALL}"
        )

        game = QuartoGame(player1=player1, player2=player2)

        while not game.player_won and not game.game_board.is_full():
            if verbose:
                game.display_boards()
            game.play_turn()

            if delay > 0:
                time.sleep(delay)

        if verbose:
            game.display_boards(exclude_footer=True)

        # Mostrar resultado de la partida
        if game.player_won:
            winner = game.winner_name
            if "Player 1" in winner:
                results[f"{player1.name} (P1)"] += 1
            else:
                results[f"{player2.name} (P2)"] += 1

            print(
                f"\n{Back.GREEN}{Fore.BLACK} RESULTADO: {winner} GANA {Style.RESET_ALL}"
            )
        else:
            results["Empates"] += 1
            print(f"\n{Back.YELLOW}{Fore.BLACK} RESULTADO: EMPATE {Style.RESET_ALL}")

        # Exportar historial con número de match
        saved_file = game.export_history_to_csv(match_number=match)
        print(f" Partida guardada como: {os.path.basename(saved_file)}")

        if match < matches:
            print(f"\n{Fore.CYAN}Preparando siguiente partida...{Style.RESET_ALL}")
            time.sleep(2)

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
