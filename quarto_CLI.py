from quartopy import logger
from quartopy import go_quarto

import click

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
    logger.info(f"Go CLI")
    go_quarto(
        matches=matches,
        player1_file=player1,
        player2_file=player2,
        delay=delay,
        verbose=verbose,
        folder_bots=folder_bots,
    )


if __name__ == "__main__":
    play_quarto()
