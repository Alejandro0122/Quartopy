from ..utils import logger
from ..models import load_bot_class
from ..game.quarto_game import QuartoGame
from ..models import BotAI

import time
import os
from colorama import Fore, Back, Style
from os import path

builtin_bot_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../bot/")
)
print(f"Directorio de bots integrado: {builtin_bot_folder}")


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
    match_dir: str = "./partidas_guardadas/",
):
    """Inicia un torneo de Quarto entre dos bots.
    Args:
        matches (int): Número de partidas a jugar.
        player1_path (str): Nombre del script del bot jugador 1 (sin extensión py), debe tener una clase ``Quarto_bot``.
        player2_path (str): Nombre del script del bot jugador 2 (sin extensión py), debe tener una clase ``Quarto_bot``.
        params_p1 (dict): Parámetros adicionales para el bot jugador 1.
        params_p2 (dict): Parámetros adicionales para el bot jugador 2.
        delay (float): Retardo entre movimientos en segundos.
        verbose (bool): Si True, muestra salida detallada de las partidas.
        folder_bots (str): Directorio donde se encuentran los scripts de los bots, default "bot/".
        builtin_bots (bool): Si True, usa bots integrados en lugar de scripts externos.
        match_dir (str): Directorio donde se guardarán las partidas, default "./partidas_guardadas/".
    Returns:
        dict: Resultados del torneo con victorias de cada jugador y empates.
    """

    print(
        f"\n{Back.BLUE}{Fore.BLACK}{' INICIANDO TORNEO DE QUARTO ':=^60}{Style.RESET_ALL}"
    )
    logger.info(
        f"Iniciando torneo de Quarto con {matches} partidas entre {player1_file} y {player2_file}"
    )
    if builtin_bots:
        logger.info(f"Usando bots integrados: {player1_file} y {player2_file}")
        folder_bots = builtin_bot_folder
    else:
        logger.info(
            f"Usando bots desde scripts: {player1_file} y {player2_file} en la carpeta {folder_bots}"
        )
    # Cargar clases de los bots
    player1_class = load_bot_class(path.join(folder_bots, f"{player1_file}.py"))
    player2_class = load_bot_class(path.join(folder_bots, f"{player2_file}.py"))
    player1 = player1_class(**params_p1)
    player2 = player2_class(**params_p2)

    results = play_games(
        matches=matches,
        player1=player1,
        player2=player2,
        delay=delay,
        verbose=verbose,
        match_dir=match_dir,
    )
    return results


def play_games(
    matches: int,
    player1: BotAI,
    player2: BotAI,
    delay: float = 0,
    verbose: bool = True,
    match_dir: str = "./partidas_guardadas/",
):
    """Juega un torneo de Quarto entre dos jugadores.
    Args:
        * matches (int): Número de partidas a jugar.
        * player1 (BotAI): Instancia del bot jugador 1.
        * player2 (BotAI): Instancia del bot jugador 2.
        * delay (float): Retardo entre movimientos en segundos.
        * verbose (bool): Si True, muestra salida detallada de las partidas.
        * match_dir (str): Directorio donde se guardarán las partidas.

    Returns:
        * match_results (list[int]): Lista con resultados de cada partida (+1 para P1, -1 para P2, 0 para empate).
    """
    print(f" Partidas: {matches}")
    print(f" Jugador 1: {player1.name}")
    print(f" Jugador 2: {player2.name}")
    print(f" Retardo: {delay} segundos\n")

    # Crear directorio para guardar partidas si no existe
    output_folder = os.path.abspath(match_dir)

    results: dict[str, int] = {
        f"{player1.name} (P1)": 0,
        f"{player2.name} (P2)": 0,
        "Empates": 0,
    }
    match_results: dict[str, int] = {}  # +1 para P1, -1 para P2, "tie" para empate

    for match in range(1, matches + 1):
        print(
            f"\n{Back.BLUE}{Fore.BLACK}{f' PARTIDA {match}/{matches} ':=^60}{Style.RESET_ALL}"
        )

        game = QuartoGame(player1=player1, player2=player2)

        _move_count = 0
        while not game.player_won and not game.game_board.is_full():
            _move_count += 1
            if verbose:
                game.display_boards()
            game.play_turn()

            if delay > 0:
                time.sleep(delay)

        if verbose:
            game.display_boards(exclude_footer=True)

        # Exportar historial con número de match
        saved_file = game.export_history_to_csv(output_folder, match_number=match)
        print(f" Partida guardada como: {os.path.basename(saved_file)}")

        # resultado de la partida
        if game.player_won:
            winner = game.winner_name
            if game.winner_pos == "Player 1":
                results[f"{player1.name} (P1)"] += 1
                match_results[saved_file] = +1
            else:
                results[f"{player2.name} (P2)"] += 1
                match_results[saved_file] = -1

            print(
                f"\n{Back.GREEN}{Fore.BLACK} RESULTADO: {winner} GANA {Style.RESET_ALL}"
            )
        else:
            results["Empates"] += 1
            match_results[saved_file] = 0
            print(f"\n{Back.YELLOW}{Fore.BLACK} RESULTADO: EMPATE {Style.RESET_ALL}")

        if match < matches:
            print(f"\n{Fore.CYAN}Preparando siguiente partida...{Style.RESET_ALL}")

    # Resumen final
    print(f"\n{Back.BLUE}{Fore.WHITE}{' RESULTADOS FINALES ':=^60}{Style.RESET_ALL}")
    print(f" Partidas totales: {matches}")
    print("-" * 60)
    for player, wins in results.items():
        print(f" {player:<15}: {wins} victorias")
    print("-" * 60)

    print(f" Todas las partidas guardadas en: {output_folder}")
    print(f"{Back.BLUE}{Fore.WHITE}{'='*60}{Style.RESET_ALL}\n")
    return match_results
