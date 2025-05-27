import importlib.util
import sys
from pathlib import Path
from .Bot import BotAI


def load_bot_class(
    file_path: str | Path, class_name: str = "Quarto_bot"
) -> type[BotAI]:
    """Importa la clase llamada ``class_name`` (no una instancia) desde el archivo especificado por ``file_path``."""
    file_path = Path(file_path)
    module_name = file_path.stem

    spec = importlib.util.spec_from_file_location(module_name, file_path)

    if spec is None or spec.loader is None:
        raise ImportError(f"El archivo {file_path} debe ser un módulo Python válido.")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    if not hasattr(module, class_name):
        raise AttributeError(
            f"Módulo {module_name} debe contener una clase '{class_name}'"
        )

    return getattr(module, class_name)
