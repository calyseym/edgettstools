import subprocess
import os
import tempfile
from pathlib import Path
import importlib.metadata
import io
import sys
from collections import namedtuple
from typing_extensions import Annotated
import typer
from gpt4all import GPT4All
import time
import pygame
import re

# Inicializar pygame para la reproducción de audio
pygame.mixer.init()

global read_initial, initial2
read_initial=False
initial2=False
print("Loading GPT4WAIFU...")
MESSAGES = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello there."},
    {"role": "assistant", "content": "Hi, how can I help you?"},
]

SPECIAL_COMMANDS = {
    "Comando reiniciar": lambda messages: messages.clear(),
    "Comando salir": lambda _: sys.exit(),
    "Comando borrar": lambda _: print("\n" * 100),
    "Comando ayuda": lambda _: print("Special commands: /reset, /exit, /help and /clear"),
}

VersionInfo = namedtuple('VersionInfo', ['major', 'minor', 'micro'])
VERSION_INFO = VersionInfo(1, 0, 0)
VERSION = '.'.join(map(str, VERSION_INFO))

CLI_START_MESSAGE = f"""

 ██████  ██████  ████████ ██   ██ ██     ██   ████     ██   ██████   ██    ██
██       ██   ██    ██    ██   ██ ██     ██ ██    ██   ██   ██       ██    ██
██   ███ ██████     ██    ███████ ██  █  ██ ████████   ██   ██████   ██    ██
██    ██ ██         ██         ██ ██ ███ ██ ██    ██   ██   ██       ██    ██
 ██████  ██         ██         ██  ███ ███  ██    ██   ██   ██       ████████
                                                           

                                                         

Welcome to the GPT4WAIFU! Version {VERSION}
Di "Comando Ayuda" para la lista de comandos

"""

# Crear aplicación typer
app = typer.Typer()

def read_message_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""

def read_initial_message():
    """Lee el mensaje inicial desde el archivo 'inicio.txt'."""
    with open("inicio.txt", "r") as file:
        initial_message = file.read()
    return initial_message

def read_initial_prompt():
    """Lee el mensaje inicial desde el archivo 'inicio.txt'."""
    with open("system_prompt.txt", "r") as file:
        initial_prompt = file.read()
    return initial_prompt

def repl(
    model: str = "Meta-Llama-3-8B-Instruct.Q4_0.gguf",
    n_threads: int = None,
    device: str = "gpu"
):
    """The CLI read-eval-print loop."""
    gpt4all_instance = GPT4All(model, device=device)

    # Configurar número de hilos si se especifica
    if n_threads is not None:
        num_threads = gpt4all_instance.model.thread_count()

        # Configurar número de hilos
        gpt4all_instance.model.set_thread_count(n_threads)

        num_threads = gpt4all_instance.model.thread_count()

    use_new_loop = False
    try:
        version = importlib.metadata.version('gpt4all')
        version_major = int(version.split('.')[0])
        if version_major >= 1:
            use_new_loop = True
    except:
        pass  # fall back to old loop
    if use_new_loop:
        _new_loop(gpt4all_instance)
    else:
        _old_loop(gpt4all_instance)
    
 
    #print(CLI_START_MESSAGE)

    use_new_loop = False
    try:
        version = importlib.metadata.version('gpt4all')
        version_major = int(version.split('.')[0])
        if version_major >= 1:
            use_new_loop = True
    except:
        pass  # fall back to old loop
    if use_new_loop:
        _new_loop(gpt4all_instance)
    else:
        _old_loop(gpt4all_instance)

def limpiar_texto(texto):
    # Expresión regular para mantener letras, números, espacios, acentos, ñ y signos de puntuación
    patron = r'[^a-zA-Z0-9\sáéíóúüñÁÉÍÓÚÜÑ.!?¿¡]'
    texto_limpio = re.sub(patron, '', texto)
    return texto_limpio

def cadena_valida(cadena):
    # Eliminar espacios en blanco al inicio y al final
    cadena = cadena.strip()
    # Verificar que no esté vacía y que contenga al menos una letra o número
    return bool(cadena) and any(c.isalnum() for c in cadena)

def mostrar_emocion(emocion):
    arte_ascii = {
        "Feliz": r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠦⣄⣠⠴⠒⠒⠉⠒⠶⣄⡏⣶⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣠⡞⣡⠀⢠⡀⠀⢦⡀⢹⣷⣼⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡿⠁⣿⠟⣷⣿⢦⡈⣇⠀⢻⣿⣈⢷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⡇⣶⣻⣀⠘⣿⣀⣹⣿⣰⣼⡟⣯⠟⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⣿⡿⠿⠋⠉⠋⠛⢿⣿⣿⡇⠈⢦⡸⣾⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⠛⣷⣄⠀⠀⠀⠀⣸⠟⠃⠉⠀⠈⢷⣩⡻⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠹⡄⠈⠙⠒⢤⣴⣾⠉⠁⣀⡀⠀⠀⠀⠹⣟⢮⡳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⠀⣿⠀⣀⣴⣿⡏⣀⡬⠟⠁⠈⣆⠀⠀⠀⠘⢧⡉⢿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡿⣿⠀⢻⣫⠉⣽⡟⠉⡅⢀⣆⠀⢠⣿⠀⠀⠀⠀⠀⠹⣦⡉⠻⢦⡀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⢗⣿⢀⡷⠁⣸⡿⠁⠀⠀⢸⣿⠃⣄⣈⡆⠀⠀⠀⠀⠀⠈⠫⣱⠦⣌⡓⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣇⣾⣿⢟⡇⢀⣿⡇⠀⢀⣰⢸⡌⢿⣿⢻⡟⣃⠀⠀⠀⠰⡂⠠⠌⠲⢤⣙⣻⠛⠓⠶⢦⡤⣄⣀⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣻⣿⠏⣾⠃⢸⢽⡇⠀⡏⠁⡶⠁⠈⣿⣎⡷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠒⠶⢤⣀⠈⠻⣄⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣴⣿⠟⠁⡼⠀⣿⠀⡟⢸⡇⢰⠃⢸⠇⠀⠀⢹⣷⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣷⣄⠘⣧⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣾⠟⠋⠀⣠⡼⢁⣼⣿⢠⣧⢾⡇⠘⡀⠸⡇⠀⠀⠘⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡉⠚⢧⠹⣷⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡴⠖⢋⣽⡿⠥⠖⠚⠉⢁⣴⣾⣿⠃⢈⠀⢸⠇⠀⠁⠀⢳⡀⠀⠀⣿⣿⣽⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠀⠀⠘⢧⡇⠀
⠀⠀⠀⠀⠀⠀⣀⣤⣾⠛⠁⣠⡼⠋⠁⠀⢀⣀⢀⣴⣿⣿⠟⠁⠀⠀⣷⠋⠂⠀⠀⠀⠀⠳⡀⠀⢹⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡿⠀⠀⠀⢸⠧⠀
⠀⠀⢀⡠⠖⠋⣩⠶⢋⡴⠋⠁⠀⠀⠿⣭⡿⣿⠿⠟⢉⣷⣄⠀⢀⣼⣿⡄⠀⠀⠀⠀⠀⢀⣹⠄⠀⢹⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠃⠀⠀⠀⠀⠐⡧
⠀⠀⣸⣄⣴⣛⣡⠞⠋⠀⠀⠀⠀⠀⠀⠀⣭⣤⣴⣾⣿⣿⣿⣷⣿⣿⣿⣷⣤⣴⣶⣾⣿⣿⣿⣆⠀⢈⣿⣷⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⢑
⠀⠰⣏⡿⢫⡞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣹⠿⠿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⢀
⠀⢀⣿⡵⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⣿⣿⣿⣿⣿⣿⣿⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⢀⡜⠀⠀⠀⠀⠀⠀⢀⠎
⢠⢸⡟⠹⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡧⠤⢙⠛⠋⠛⠛⠿⠿⢿⡟⠛⠉⠁⠀⠀⠀⠀⠀⠠⠐⠀⠀⠀⠀⠀⠀⠀⢀⡼⢀⠀⠄⠀⠀⡀⡀⠀⠀
⢸⣎⡇⠀⠳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢷⠀⡀⢰⡅⠀⠀⠀⠀⠀⡝⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⡿⢋⠞⠀⢠⣮⠎⠀⠀⠀
⠀⢿⣷⠀⠀⠈⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣶⣿⣇⠀⠀⠀⠀⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡾⠋⣠⠋⢀⣴⠟⠁⠀⠀⠀⠀
⠀⠘⣏⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⢹⣻⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠟⢡⠞⣁⣴⠟⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠸⡄⠳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠳⢄⡀⠀⠀⠘⣿⣿⡯⢶⢧⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡾⢁⣴⠿⠚⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "Triste": r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣤⣤⣤⣤⣄⣀⠀⠀⠉⠣⠙⣳⢤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⣴⡰⠁⣼⠿⢶⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⠶⡀⣤⢺⣿⡯⠶⠧⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⠴⠶⠶⠒⠲⠤⠶⢤⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢤⣈⢛⣤⣾⡷⠶⠶⠶⠧⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣶⣾⣍⠀⠀⠀⠀⠀⠀⢠⡆⣧⣄⣉⡛⠛⠿⣿⣿⣿⣿⣿⣿⡿⠿⢴⣒⣛⣥⡆⣠⠀⠀⠀⠀⠀⠀⠈⣶⣴⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⡧⡞⣳⣶⢶⡶⢰⣯⢸⢳⡘⣿⣿⣿⣿⡏⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⣤⣳⢡⢿⢈⣷⠀⣴⣧⣀⡀⢿⣿⣿⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⠙⣗⣧⣋⡇⠘⢛⣿⣿⠞⢸⣷⡘⣿⣿⡿⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢳⣿⣿⣦⣿⣶⣿⣷⢾⣹⣶⣾⠝⠳⣄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣠⠞⠀⠀⠀⣹⠃⠀⠀⠀⠘⠛⠀⢀⣿⣿⣿⣾⣿⣧⣦⣬⣿⣿⣿⣿⣻⣿⣿⣿⣿⣷⣿⣿⣿⠘⢿⣿⣿⡎⢿⣏⠻⣍⠀⠀⠈⢦⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⡴⠋⠀⠀⠀⡼⠃⠀⠀⠀⠀⠀⠀⠀⣽⢹⣿⣿⣿⡏⢿⣯⣿⠋⠙⠙⠟⠿⣿⣽⡏⣿⣿⡏⣿⣿⡌⣆⠙⢿⣷⠈⣏⢦⣸⣦⠀⠀⠀⠹⣄⠀⠀⠀⠀⠀
⠀⠀⠀⢠⠞⠀⠀⠀⠀⡼⠁⠀⠀⠀⠀⠀⠀⠀⣸⠃⣸⣿⣿⣿⣷⡘⠛⠉⠀⠀⠀⠀⠀⠙⠋⣸⣿⣿⣿⣿⣿⡇⢿⡄⠀⢹⣀⣸⣿⡇⠙⢧⠀⠀⠀⠈⢣⡀⠀⠀⠀
⠀⠀⡴⠃⠀⠀⠀⠀⡼⠁⠀⠀⠀⠀⠀⠀⠀⣰⡇⡸⣿⣿⣿⣿⣿⡻⣆⠀⠀⠀⠀⠀⠀⠀⡰⢿⣿⣿⣿⣿⣿⣧⠈⣇⠀⠸⠋⠙⢿⣿⣦⡀⢳⠀⠀⠀⠀⠙⣄⠀⠀
⠀⠼⠁⠀⠀⠀⠀⡼⠁⠀⠀⠀⠀⠀⠀⠀⢰⢻⢧⢣⣿⣿⣿⣿⣿⣿⣮⣀⠈⠉⠒⠺⠗⣨⣶⣿⣿⣿⣿⣿⣿⣿⠀⠞⡆⠀⠀⠀⠈⣿⣿⡷⡀⢣⠀⠀⠀⠀⠘⣆⠀
⠀⠀⠀⠀⠀⢀⡴⠓⠦⣄⡀⠀⠀⠀⠀⣠⣏⣸⡏⣼⣿⣿⣿⣿⣿⣿⣿⣿⣙⣲⣤⣖⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⡦⣥⣹⠀⠀⠀⢀⣿⣿⡧⠷⠚⢦⡀⠀⠀⠀⠈⣆
⠲⠤⣀⠀⠀⠉⠀⠀⠀⠀⠈⠉⠒⠒⢦⠿⣧⠀⠉⠉⠙⢿⠻⣿⣿⣿⠿⣏⡛⠯⠭⠽⢛⡝⢿⣿⣿⣿⣿⡿⠉⠀⢰⣿⡿⠤⠔⠒⠚⠉⠁⠀⠀⠀⠀⠙⠀⠀⣀⡤⠞
⠀⠀⠈⠑⠢⢄⣀⠀⠀⠀⠀⠀⠀⠀⠘⣆⣼⡆⢀⣀⣠⣼⣶⣿⣿⣿⡦⣵⣍⡓⠒⣚⣭⣮⡾⣽⣿⣿⣿⣃⣠⣤⠾⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠴⠚⠉⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠙⠒⠤⣀⡀⠀⠀⠀⠹⣿⠛⠉⠉⠉⢹⣹⠺⡏⣿⣷⣷⣯⣿⣿⣫⣿⡯⣲⣿⣿⣿⠏⠉⠀⠀⠀⣟⡟⠀⠀⠀⠀⢀⣠⠴⡞⣩⠄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⠲⣤⣸⣿⡆⠀⠀⢀⣼⡟⢓⡿⢼⣿⣳⡙⠿⡿⠟⣡⠞⣹⣿⣿⡟⠻⣄⠤⠤⣤⣿⣄⣠⠤⣶⣾⣿⣿⣾⣞⣋⡴⠃⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⡏⠀⠀⠤⠶⠿⣧⠼⠇⠀⣿⣇⠻⣶⠬⠘⢁⣞⣿⣿⡿⣶⡞⠁⠀⠀⠀⣼⣿⡌⢣⡹⣿⣿⣿⣭⡭⢟⡁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⡿⣽⣿⣿⡀⢀⣠⡤⠄⢹⡀⢀⡄⣿⣿⠛⠒⣖⠋⢿⣼⣿⣿⠃⠺⣷⣄⠀⠀⠚⠿⣿⣿⡄⠳⣄⢻⠉⠉⠛⠋⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡟⣱⣿⣿⣿⡿⠛⠉⠀⣀⢹⢷⣾⣾⣿⣿⠸⡟⠉⣻⠎⣿⣿⣿⠀⠀⠀⠙⢧⣄⢀⣼⣿⡏⢿⡄⠹⣮⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⠋⢠⣿⣿⣿⣿⣷⣀⡤⠞⢁⣈⣷⣿⣿⣿⣿⠀⢳⠟⡟⢠⣿⣿⣿⣆⠀⠀⠀⠈⢻⣿⣿⣿⣿⠘⣷⠀⠹⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢠⡞⢹⠀⣾⢻⣿⣿⣿⣿⣿⠀⢠⣝⣻⣿⣿⣿⣿⡏⠀⠈⣾⡄⢸⣿⣿⣿⣿⣿⣶⠶⣾⣿⣿⣿⣿⣽⠀⢹⡇⠀⢸⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢠⠏⠀⢸⣸⡏⢸⣿⣿⣿⣿⣿⣿⣾⣭⠿⠿⠟⣻⡿⠀⠀⠀⣷⣧⠈⣿⡻⢿⢿⢿⣿⠟⣿⣿⣿⣿⣿⢸⡄⠈⣷⠀⣸⠙⣧⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢠⡟⠀⠀⣼⣿⠁⡿⣏⣿⣿⣿⣿⣿⣿⣷⣤⣤⣌⣡⣇⣀⠀⠀⣿⣿⣀⣈⣳⣼⣟⣋⡿⢰⣿⣿⣿⣿⡟⢸⠁⠀⣿⢠⡏⠀⢹⡆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠸⡇⠀⢰⠁⣿⡀⢻⠹⣿⣿⡜⣿⣿⣿⣧⢻⡳⡶⣴⠥⢿⡿⠿⣿⣿⣿⣧⠼⣿⠉⣽⡀⣿⣿⣿⡟⣼⠁⣾⠀⠀⣿⠏⠀⠀⢘⡇⠀⠀⠀⠀⠀⠀⠀
        """,
        "Enojada": r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⡇⢀⣀⣠⠤⠴⠶⢶⣶⠤⡤⣄⡀⣸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⣿⠊⠉⠁⠀⠀⠒⢶⡉⠻⠕⠇⢈⣩⣿⣿⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠉⠀⠀⠀⣾⣿⣿⠈⠻⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⡰⠋⢸⡿⠛⢋⣉⣩⠉⣀⢤⣭⡉⠉⠐⠤⣀⠀⢸⣿⣿⣿⢣⠀⠀⠙⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢠⠞⢀⡔⠃⠀⠚⣭⡴⠂⠀⠀⢻⣬⣝⠳⣤⠀⠀⢳⣟⢿⣿⣿⠈⢣⠀⠀⠈⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢠⠏⡰⠋⠀⠀⢀⡼⠋⠀⠀⡞⠀⠀⠹⣎⠱⣌⠳⣄⠀⢷⠱⡹⣿⠀⠘⠃⠀⠀⠈⢷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⢏⡎⢠⡾⠀⢀⣾⠁⠀⠀⠀⡇⠀⠀⠀⢻⡄⢻⠳⡈⠃⢸⡇⠸⣽⡀⠀⢠⠀⠀⠀⠸⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⡜⡸⠀⡾⠁⠀⢨⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⡆⠈⡌⢏⢆⠈⣿⠀⢰⣣⠀⢸⠀⠀⠀⠀⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢧⠇⢸⠇⠀⡰⣿⠀⠀⠀⠀⠀⣇⠀⢀⠀⠀⠘⠀⢣⠈⢎⢣⡏⡇⠀⠏⡇⠘⣇⠀⠀⠀⢸⣇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⡾⠀⡾⢀⡜⠁⢻⢰⠀⠀⠀⠀⣿⠀⢸⣆⠀⠀⠀⠘⠀⠈⡆⡇⡇⠀⠸⢰⠀⣿⠀⠀⠀⢸⢸⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢠⡇⢠⢇⣎⠀⠢⣸⠏⡆⠀⠀⠀⢸⡆⢸⠻⣦⠀⠀⢀⡇⠀⠸⡇⢻⡆⠀⠘⣆⣻⠀⠀⠀⢸⠀⡆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢸⠁⠈⣼⠾⠗⣶⣿⡼⣴⠀⠀⠀⠈⣧⢸⠀⠈⢷⠀⠈⢷⠀⠀⠁⠀⢻⡄⠀⣧⢿⠀⠀⠀⢸⠀⣷⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢸⠀⢸⢻⣇⠸⣿⣺⣧⢹⣣⠀⠀⠀⢻⢸⠀⣀⣀⢑⣄⡘⣷⡀⠀⠰⡄⢳⡄⢈⢿⠀⠀⠀⡟⡇⢸⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢸⠀⠸⡎⠸⠳⠼⠿⠉⢇⢻⢦⠀⠀⠘⣽⣰⡶⣶⣶⣤⣙⣯⣻⡇⢀⠈⠘⣿⣾⣝⠇⠀⠀⠇⢳⡜⡀⠀⠀⠀⠀⠀⠀
⠀⠀⢸⠀⠀⡇⠀⠀⠀⠀⠀⡼⢆⢫⠁⠀⠀⠹⠁⠀⣇⣏⣓⣿⠿⣿⣿⠘⢻⣿⡎⢸⢿⢸⠀⢰⢀⠘⢷⡅⠀⠀⠀⠀⠀⠀
⠀⠀⠈⠀⠀⢁⠀⠀⠀⠀⡼⠁⠈⢣⣣⠀⠀⠀⡇⠛⢦⣍⣭⡥⠢⠀⢸⠚⠋⡭⢋⡬⢊⠎⠀⡘⡏⠀⣟⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⡄⠀⢸⣆⠀⠀⠠⠄⣀⠀⠀⠹⣷⠀⠀⢻⠀⠀⠈⠀⠀⠀⠀⣸⠀⠀⢒⣠⣶⣿⠀⠀⡟⠇⠀⢹⣷⠀⠀⠀⠀⠀⠀
⠀⢀⡴⡇⠀⠈⠙⢆⠀⢠⣄⣀⠀⠀⠀⢹⡆⠀⣸⠀⠀⠀⠀⠀⢀⣴⣿⠰⣶⣿⣿⣿⣿⠀⢠⢿⠀⠀⠈⣿⡆⠀⠀⠀⠀⠀
⢠⠋⠀⠃⠀⢰⠀⠘⣆⠘⡏⠉⠙⢲⣶⡤⣿⢸⡏⠀⠀⢀⣠⣶⣿⣷⣿⢀⣟⢿⣿⣿⡏⠀⢸⣾⡄⠀⠀⢿⣧⠀⠀⠀⠀⠀
⢿⠀⠀⢸⠀⢸⠀⠀⣿⣆⣇⠀⡤⠚⠋⠁⡿⢋⣡⣴⣾⣿⣿⣿⣿⣿⣿⢸⠋⣽⡿⣿⡇⠀⢸⣿⣿⡀⠀⠘⣿⠀⠀⠀⠀⠀
⠘⣆⠀⢸⠀⢸⠀⠀⢻⡏⠻⣍⣀⣤⣤⣶⣿⣿⣿⣿⣿⣿⣯⣿⣿⣿⣿⢰⠺⣿⣿⣿⡇⠀⡟⠙⠿⣷⠀⠀⣿⡃⠀⠀⠀⠀
⠀⠹⣆⠘⡆⣼⠀⠀⠈⢃⠀⠀⣰⣿⣇⠙⡟⣻⠿⣿⣿⣿⣿⢿⣿⣿⣿⠰⣟⣿⣿⣿⠃⢠⠇⠀⠀⠈⢧⡀⢸⣇⠀⠀⠀⠀
⠀⠀⠹⡄⡇⣿⠀⠀⠀⢸⣀⣼⣿⣿⣿⣄⡟⣽⣧⠀⠉⠛⠻⠿⠿⡿⢿⠸⠛⠉⠁⠸⠀⡜⠀⢀⠖⠀⠀⠙⢦⣿⠀⠀⠀⠀
⠀⠀⢀⣵⡇⡇⡇⠀⠀⢀⡋⠉⠉⣿⣷⣶⣾⢿⣿⣷⣀⠀⠀⢀⡜⠀⢸⠀⠀⠀⠀⡄⡸⠁⠀⣡⠆⠀⢀⣤⠀⠻⣧⠀⠀⠀
⠀⣰⣿⣿⡇⡇⡇⢀⣴⠿⠒⠈⠁⢻⣿⣿⡏⠀⠈⠙⠻⢦⢀⠞⠀⠀⢸⡄⠀⠀⢠⢷⠃⢀⠞⠁⠀⣴⣿⠞⠀⠀⠈⢧⠀⠀
        """,
        "Preocupada": r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣤⣿⣿⣿⣤⡀⢀⣤⣤⠀⢀⣠⣴⣶⣦⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣾⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣿⣻⣿⣿⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⡿⠟⠉⠉⠉⠉⠙⠛⠿⣿⣿⣿⣿⣟⣶⣾⡏⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⡿⣻⡿⠔⠒⠓⠀⠀⠀⠀⠒⠒⢼⣿⣿⣿⢹⣟⣿⡄⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⢁⣠⣀⣤⡀⠀⠀⠀⠄⣀⣀⡟⢿⣿⣾⣿⣿⣷⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠀⢸⣿⣯⠟⣁⣈⡙⠇⠀⠀⠐⠛⢫⠙⠻⣾⣿⣿⣽⡷⣽⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣨⣿⡿⢾⣷⣶⣿⠀⠀⠀⢠⣿⣤⣽⡄⠸⣿⡿⠿⢇⠈⢳⣆
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣗⢻⡇⠈⠛⠛⠁⠀⠀⠀⠈⠛⠻⠟⠁⢠⣿⣷⣴⡈⡇⠀⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢯⣹⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⡗⣱⠃⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⡟⣦⠀⠀⠀⠀⠲⠀⠀⠀⠀⠀⣰⣿⢿⣿⣿⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣧⣿⣷⢦⡀⠀⠀⠀⢀⣀⡤⢚⣿⣿⣾⠋⣿⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠁⢿⡿⣿⣷⣌⡓⠒⠊⢉⣀⣴⣿⣿⡟⢿⠀⠈⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠃⣸⣿⣿⣿⠀⣾⣿⣿⣿⣿⡿⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡔⢁⣿⣿⡿⣴⣿⣿⣿⣯⡾⠀⠈⢷⡄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠋⠀⣸⢿⣽⡿⠻⣿⣿⣿⣿⠇⠀⠀⠀⡿⣆⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠇⠀⣠⣿⣸⣿⣤⣴⣿⣿⣿⣿⠀⠀⠀⢰⠀⠘⡆⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠋⢀⣴⣿⣿⢿⣿⣿⣿⣿⠀⣀⡏⠀⠀⠀⢸⠀⠀⢸⡀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡏⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣤⣤⡇⠀⠀⠀⡜⠀⣠⠋⣧⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⠁⢿⣿⣿⣿⣿⣇⢀⣯⣿⣿⣿⣿⠀⠀⠀⠀⡇⡴⡇⠀⢸⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠎⡞⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⢀⠏⢀⠇⠀⢸⡄⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡎⢀⡷⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⡎⠀⢸⠀⠀⠀⡇⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠀⢸⠑⢀⣾⣧⣿⣿⣿⣿⡀⢨⣿⣿⣿⣿⠃⠀⡜⠀⠀⡸⠀⠀⠀⣿⡄
        """,
        "Exitada": r"""
⠀⠀⠀⠀⣀⢀⣠⣤⠴⠶⠚⠛⠉⣹⡇⠀⢸⠀⠀⠀⠀⠀⢰⣄⠀⠀⠀⠀⠈⢦⢰⠀⠀⠀⠀⠀⠈⢳⡀⠈⢧⠀⠀⠀⠀⢸⠀⠀⠀⠀
⠀⠀⠉⠀⠀⠀⡏⠀⢰⠃⠀⠀⠀⣿⡇⠀⢸⡀⠀⠀⠀⠀⢸⣸⡆⠀⠀⠀⠰⣌⣧⡆⠀⢷⡀⠀⠀⣄⢳⠀⠀⢣⠀⠀⠀⢸⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡇⠀⠘⠀⠀⠀⢀⣿⣇⠀⠸⡇⣆⠀⠀⠀⠀⣿⣿⡀⠀⠀⠀⢹⣾⡇⠀⢸⢣⠀⠀⠘⣿⣇⠀⠈⢧⠀⠀⠘⠀⢠⠀⠀
⠀⠀⠀⠀⠀⢀⡇⠀⡀⠀⠀⠀⢸⠈⢻⡄⠀⢷⣿⠀⠀⠀⠀⢹⡏⣇⠀⣀⣀⠀⣿⣧⠀⢸⠾⣇⣠⣄⣸⣿⡄⠀⠘⡆⠀⠀⠀⠀⠆⠀
⠀⠀⠀⠀⠀⣾⢿⠀⠇⠀⠀⠀⢸⠀⠀⢳⡀⢸⣿⡆⠀⠀⠀⣬⣿⡿⠟⠋⠉⠙⠻⣽⣀⡏⠀⠙⠃⢹⡙⡿⣷⠀⠀⢹⠀⠀⠀⠀⠰⠒
⠀⠀⠀⠀⢸⣿⣿⣇⢸⠀⠀⠀⢸⣦⣤⡀⣷⣸⡟⢧⣀⡴⠶⠿⠻⡄⣀⣤⣴⡾⠖⠚⠿⡀⠀⠀⠀⠈⣧⠁⠹⠆⠀⠀⣇⠀⠀⠀⠀⠀
⠀⠀⠀⢀⢸⣀⣼⣿⣼⡆⠀⢀⡘⡇⠀⠀⠹⡟⢷⡜⢉⣠⣠⣠⣀⣤⡿⣛⣥⣶⣾⡿⠛⠿⠿⣶⣦⡤⢹⠀⢀⠀⠀⠀⢹⡄⠀⠀⠀⠀
⠀⠀⠀⢸⢸⡛⠁⠀⠙⢿⠋⠉⠉⠻⠀⠀⠀⢿⣄⠈⠁⠀⠀⠀⢉⢟⣴⡿⠿⠟⢁⠇⠀⠀⠀⠀⠹⣿⠻⡇⢸⠀⠀⠀⠈⣷⠀⠀⠀⠀
⠀⣀⣀⣘⣿⡇⠀⢀⣠⣤⣶⣶⣶⣾⣦⡀⠀⠈⡿⠀⠀⠀⠀⠀⠀⣿⠟⠳⠦⡤⠊⠀⠀⠀⠀⠀⣸⠇⠀⡇⣼⠀⢰⠀⠀⢹⣇⠀⠀⠀
⠛⠁⠈⣿⣷⣧⣴⣿⠿⠛⣿⠿⣿⣿⡿⠗⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⣠⣴⣶⠿⠿⠿⡷⢛⠕⠷⡄⣧⣿⠀⢸⠀⠀⠸⣿⡄⠀⠀
⠀⠀⢠⣿⢿⣿⣿⠁⠀⠀⠈⠳⠤⠶⠃⠀⠀⢰⡀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣿⠟⣱⠒⡠⢆⡴⣣⣯⢞⣴⡟⢿⡄⡏⠀⠀⠀⡏⢷⡀⠀
⠀⠀⡌⣿⠀⠙⣿⡦⢀⣤⡴⣶⠖⣲⠆⢀⠞⠁⠱⠀⠀⠀⠀⠀⠠⣾⠟⠛⡡⠞⠁⢀⡴⢋⢎⣽⡿⣫⠋⠀⠘⢷⠃⡄⠀⠀⡇⠈⣿⡀
⠀⠀⣇⢹⣦⠀⠼⢃⡾⢋⣶⢃⡼⣹⡳⠃⠊⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠈⠠⠋⠀⡰⠋⠀⢘⣇⡇⠀⢠⠟⠀⡇⠀⠀⠀⠀⢹⡵
⠀⠀⢻⣌⢿⡆⠀⡝⣼⠟⣩⢏⣾⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠞⠀⠀⠀⠀⠈⠀⣠⠏⣠⣾⡇⠀⠀⠀⠀⠘⣷
⡀⠀⢸⣿⣿⣷⠆⢠⠏⡴⠃⡡⠋⠀⠀⠀⠀⠀⠀⣀⣠⠤⠔⠒⠤⣄⣀⠀⠀⢀⣰⠏⠀⠀⠀⠀⢀⣠⡾⠗⠋⢰⠏⡇⠀⠀⠘⠀⠰⢻
⣇⠀⠘⣿⣿⣟⠻⣄⡞⠀⠐⠁⠀⠀⠀⠀⠀⣠⠞⣩⣤⣶⣶⣾⣷⣶⣬⣿⣿⣿⡏⠀⠀⠀⠀⠉⠉⠁⠀⠀⠀⢸⡆⡇⠀⠀⠀⠀⠀⠀
⠹⡄⠀⠹⣿⣿⡄⠀⠉⠉⠀⡀⠀⠀⠈⢻⣾⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣇⣧⠀⠀⠀⠀⠀⠀
⠀⣿⢦⣀⠘⢿⣷⡀⠀⠀⡀⢦⠀⠀⠀⠀⠹⣿⣿⠏⠙⢻⣿⡿⠛⠉⠀⠸⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⠀⠀⡆⠀⠀⡀
⢼⣿⠀⠈⢳⣤⣉⣻⣤⣀⣉⣩⠆⠀⠀⠀⠀⠹⡿⠀⠀⠈⡿⠀⠀⠀⠀⣸⡇⠀⠀⠀⠀⠀⠀⠓⠂⠀⣠⣾⣿⣿⡿⢿⡄⠀⣧⠀⠀⠹
⣾⠃⠀⣠⣿⣿⣿⣿⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⢸⡇⠀⠀⢠⠴⣿⡄⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⡿⣧⣀⠧⣰⣻⢄⠀⠀
⠛⠶⢾⣿⣽⣭⣽⣭⢹⣷⠀⢹⣦⣀⠀⠀⠀⠀⡄⠀⠀⣸⡀⠀⠀⠁⣰⣧⣽⠀⠀⠀⠀⢀⣴⣾⣿⣿⡟⣻⣿⣿⣿⣿⢠⣿⣧⡸⣷⣄
⠀⠀⠀⠈⠙⠿⣿⣿⣿⠏⠀⣾⣿⣿⣷⣦⣀⠀⢇⠀⠀⠈⠁⠀⣠⠔⠁⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠏⣼⣿⠏⣷⡈⠉
⠀⠀⠀⠀⠀⠀⠀⠙⠻⣶⣾⣿⣿⣿⣿⣿⣿⣷⣾⡆⠀⠀⠀⡾⠁⠀⠀⠀⣀⡴⠞⠛⣛⣿⡿⠿⠛⠛⠉⠉⠀⠀⠀⢰⣿⡿⠂⠈⠻⡄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢎⠉⠛⠻⠿⠿⠿⠿⠿⣇⠠⠸⣇⣀⣤⣴⣾⡭⠶⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⠇⠀⠀⠀⠘
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⣤⡀⠀⠀⠀⠀⠀⠈⣳⠀⣿⠛⠻⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⡯⠀⠀⠀⠀⠀
        """,
        "Neutral": r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠤⠤⠠⡖⠲⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠐⠀⠀⠀
⠀⠀⠀⠀⠀⡠⠶⣴⣶⣄⠀⠀⠀⢀⣴⣞⣼⣴⣖⣶⣾⡷⣶⣿⣿⣷⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄⠀⠉⠀⠀⠀⠀
⠀⠀⠀⠀⢸⠀⠀⠀⠙⢟⠛⠴⣶⣿⣿⠟⠙⣍⠑⢌⠙⢵⣝⢿⣽⡮⣎⢿⡦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄⠀⠀⠂⠁⠀⠀⠀⠀
⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⢱⡶⣋⠿⣽⣸⡀⠘⣎⢢⡰⣷⢿⣣⠹⣿⢸⣿⢿⠿⡦⣄⠀⠀⠀⠀⠀⠀⡠⠀⠀⠂⠂⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⢧⡿⣇⡅⣿⣇⠗⢤⣸⣿⢳⣹⡀⠳⣷⣻⣼⢿⣯⡷⣿⣁⠒⠠⢄⡀⠀⠀⡀⠀⠁⠄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⣼⣿⣧⡏⣿⣿⢾⣯⡠⣾⣸⣿⡿⣦⣙⣿⢹⡇⣿⣷⣝⠿⣅⣂⡀⠀⠡⢂⠄⣈⠀⠄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠇⠀⠀⠀⠀⣿⡟⣿⡇⡏⣿⣽⣿⣧⢻⡗⡇⣇⣤⣿⣿⣿⣧⣿⣿⡲⣭⣀⡭⠛⠁⠀⠀⣨⠁⠉⣂⢄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠸⠀⠀⠀⠀⢻⣿⣇⣥⣏⣘⣿⣏⠛⠻⣷⠿⡻⡛⠷⡽⡿⣿⣿⣿⣷⠟⠓⠉⠢⢄⡀⢠⠇⠀⠀⠀⠁⠫⢢⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢇⠀⠀⠀⢸⣾⣿⣽⣿⣏⣻⠻⠁⢠⠁⠀⠀⠀⠘⣰⣿⣿⢟⢹⢻⠀⠀⠀⠀⠀⠈⡒⢄⡀⠀⠀⠀⠀⠀⠀⠑⢄
⠀⠀⠀⠀⠀⠀⠘⡄⠀⠀⢸⣯⣿⣿⣿⢷⡀⠀⠀⠀⠀⠀⠀⠀⠛⣩⣿⣿⢿⣾⣸⠀⠀⠀⠀⠀⠀⣅⡠⠚⠉⠉⠁⠀⠀⠀⢀⠌
⠀⠀⠀⠀⠀⠀⠀⢡⠀⠀⠀⢟⣿⣯⡟⠿⡟⢇⡀⠀⠀⠐⠁⢀⢴⠋⡼⢣⣿⣻⡏⠀⠀⠀⣀⠄⠂⠁⠀⠀⠀⠀⠀⠀⢀⡤⠂⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠇⠀⠀⠈⠊⢻⣿⣜⡹⡀⠈⠱⠂⠤⠔⠡⢶⣽⡷⢟⡿⠕⠒⠀⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⡠⠐⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠘⡄⠀⠀⠀⠀⢿⠿⠿⢿⠾⣽⡀⠀⠀⠀⠈⠻⣥⣃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⠒⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⡀⡀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣖⠂⠠⠐⠋⠀⠙⠳⣤⣠⠀⠀⠀⣀⠤⠒⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠵⡐⠄⠀⠀⠀⠀⠀⠀⠀⠈⢷⣄⡀⠀⠠⡀⠀⠈⠙⠶⣖⡉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡥⠈⠂⠀⠀⠀⠀⠀⠀⠀⣼⠉⠙⠲⣄⠈⠣⡀⠀⠀⠈⢻⡦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡄⠀⠀⠀⠀⠀⠀⠀⢠⠇⠀⠀⠀⠈⣷⡄⠈⠄⠀⠀⠀⢧⠀⠑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡄⠀⠀⠀⡀⠀⢠⣿⣤⣤⣶⣶⣾⣿⣿⡄⢸⠀⠀⠀⢸⣄⣤⣼⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡄⠀⠀⠇⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⢸⠀⠀⠀⣼⣿⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣀⣀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⢀⣼⣿⣿⣿⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠉⠁⠀⠈⠉⠙⠛⠿⠿⠽⠿⠟⠛⡉⠛⠲⣿⣿⠿⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡇⠀⠀⢠⡏⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠋⠀⠀⣠⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢔⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "Curiosa": r"""
⠀⠀⠀⠀⣿⣿⣿⣿⣿⣟⣿⡏⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣿⣿⣿⣿⠟⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣿⣿⣿⣇⡀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢿⣿⣿⣟⣃⡤⠤⠿⠿⣿⣿⣿⣿⣿⣿⣿⡿⢿⣴⡶⠦⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢸⣿⣿⠟⠁⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⡆⠀⢿⣿⠁⠀⠀⠈⢦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢸⣿⠯⠀⢠⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣧⠀⣿⡏⠀⠀⠀⢠⡀⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠸⣿⠀⠀⠘⡆⠀⣰⣿⣿⣿⣿⣿⣿⣿⣜⣷⣿⠁⠀⠀⠀⢸⡇⣸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢻⠀⠀⠘⣿⢠⣿⣿⣿⣿⣿⣿⣟⠿⢿⠛⠁⠓⠆⠀⠀⣼⠁⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠘⡄⠀⠀⣾⣾⣷⣿⣿⣿⠿⢿⣿⣶⣾⣶⣶⣾⣷⣶⣶⣿⠘⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡇⠀⠀⢹⣇⣾⣿⢿⡟⠀⠸⣿⡄⢹⡁⠀⠀⠀⠀⠈⢹⢰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡇⠀⠀⢸⣿⡟⠉⠘⣇⠀⠀⠉⠙⠺⡇⠀⠀⠀⠀⡓⠘⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣷⠀⠀⣼⡿⠧⠒⠒⠛⠛⠒⣶⢤⣄⣳⡀⣀⣀⡤⠥⠤⠬⢷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣾⡤⠞⠉⠀⠀⠀⠀⠀⠀⠀⠀⠁⢹⣿⣿⡿⠑⠀⠀⠀⠀⠀⠈⠙⠓⠢⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢰⢋⣷⠊⠀⠀⠴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠳⣌⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢀⣯⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢻⡤⢄⡀⠀⠀⠀⠀⠀⠀⠀
⢠⡴⢻⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣗⡇⠀⠀⠀⠀⠀⠀⠀
⠈⣷⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⡇⠀⠀⠀⠀⠀⠀⠀
⠈⢿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣇⠀⠀⠀⠀⠀⠀⠀
⠀⣾⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⠀⠀⠀⠀⠀⠀⠀
⠀⢹⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣷⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡿⠀⠀⠀⠀⠀⠀⠀
⠀⠸⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡾⣿⣿⣿⡟⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⠇⠀⠀⠀⠀⠀⠀⠀
⠀⢀⡷⠖⠒⠲⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠚⢁⣢⣿⡿⡿⣇⠈⠙⠢⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢞⡞⠀⠀⠀⣀⣀⡀⠀⠀
⢠⠞⠀⠀⠀⠀⠀⠹⣶⢤⡀⠀⠀⠀⠀⠀⠀⣸⡇⠀⠀⠀⠈⡇⢀⠔⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠀⢀⡴⠊⠁⠀⠈⢦⡀
⡞⠀⠀⠀⠀⠀⠀⠀⠙⠳⣽⣷⡀⠀⠀⠀⠀⣿⠇⠀⠀⠀⠀⡇⢻⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⢷⣶⡿⠀⠀⠀⠀⠀⠀⢧
⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⢦⡀⠀⢠⢿⠀⠀⠀⠀⠀⢧⠈⠀⠀⠀⠀⣀⡤⠤⠤⠤⣴⣻⣳⠋⠀⠀⠀⠀⠀⠀⠀⠀⣾⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "Sorprendida": r"""
⣿⣿⣿⣿⣿⣿⡿⠋⠁⠀⠀⠀⢀⣾⡿⠋⠉⠁⢠⣿⠏⢁⣿⣿⣿⠏⠉⢸⣿⡏⠉⢻⣿⣿⡇⠈⠙⢿⣿⣿⣿⣷⡆⠀⠀⢇⠢⣈⡒⡤
⣿⣿⣿⣿⣿⣏⣴⡇⠀⠀⠀⢠⡿⠋⠀⠀⠀⣰⣿⠋⠀⣼⣿⣿⠏⠀⠀⡾⣿⠁⠀⠀⣿⣿⣷⠀⠀⠀⠹⣿⣿⣿⣿⣄⢀⣿⣷⣿⣶⣶
⣿⣿⣿⣿⣿⣿⡿⠀⠀⠀⢠⡟⠁⠀⠀⠀⢰⣿⠇⠀⢰⣿⣿⡷⠀⣀⣜⣁⣻⣀⣀⣀⣸⢻⣿⡇⠀⠀⠀⠘⣿⣿⣷⠹⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠃⠀⠀⣠⣿⠀⠀⠀⠀⢠⣿⡏⠀⢀⣿⣿⡿⠛⣩⣿⠿⠛⢻⡏⠉⠉⢹⠉⢿⣿⡀⠀⠀⠀⠹⣿⣿⡆⠙⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⡏⠀⠀⣰⣿⡟⠀⠀⠀⢀⣾⣿⠀⠀⣸⣿⡿⢥⣶⠝⠁⠀⠀⠀⡇⠀⠀⡜⠰⡀⢻⡇⠀⠀⠀⠀⢿⣿⣿⠀⠸⣿⣿⣿⡿
⣿⣿⢿⣿⣿⡃⠀⣼⣿⣿⡇⣀⣀⣤⣾⣿⡇⠀⠰⣼⡟⣠⠎⠁⠀⢀⣠⠔⠁⢹⣀⣠⣧⣶⣦⣤⣷⣤⣤⣠⣤⠼⣿⣿⡆⠀⢹⣿⣿⣿
⣿⣿⣿⣿⣿⠀⣼⣿⣿⣿⣏⣁⣼⣿⣿⣿⠀⢠⣾⣟⡔⠁⠀⠀⠀⢸⠁⠀⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⣿⣿⣇⠀⠀⣿⣿⣿
⣿⣿⣿⣿⣿⣸⣿⣿⣿⣿⣟⣹⣿⣿⣿⡿⣴⣿⡿⠋⠀⠀⠀⠀⠀⠀⢰⣾⢟⣻⡿⠛⢻⢋⣻⣏⣱⠞⠙⣄⡀⠀⣿⡽⣿⠀⠀⢸⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠉⢘⡅⠚⠋⠉⠁⠀⠀⠀⠀⣔⣾⢏⢦⢄⣿⣧⣿⡆⠀⠈⣿⣿
⣿⣿⣿⣿⣿⡿⢸⣿⣿⣿⡿⢻⣿⣿⡿⠋⠀⠀⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⠟⠉⠀⢂⢻⣿⣿⣿⡇⠀⠀⢽⣿
⣿⣿⣿⣿⣿⢃⣿⣿⣿⣿⣷⣿⣿⣿⣿⡷⠀⠀⡸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠉⠀⢀⣠⣾⣟⡖⢻⣿⣿⠃⠀⠀⣿⣿
⣿⣿⣿⣿⣟⣼⣿⣿⣿⣿⣿⣿⠟⣻⠿⠓⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⠾⠿⠛⠉⠁⢰⢸⣿⡿⠀⠀⠀⣿⣿
⣿⣿⣿⣿⣿⣿⣿⠋⠰⢟⣿⠌⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠇⠀⠀⢠⡇⣿
⣿⣿⣿⣿⣿⣿⣏⠓⠓⠚⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠿⠿⠿⢾⣿⡟⠀⠀⠀⣼⠃⣿
⣿⣿⣿⣿⣿⣿⣿⣷⢦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡤⠤⠤⠤⠤⠤⠄⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡿⠀⠀⠀⣰⠏⢰⣿
⣿⣿⣿⣿⣿⣿⣿⣿⡀⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⣠⢚⣡⣴⣾⣿⣿⣿⣿⡿⠿⢿⠀⠀⠀⠀⠀⠀⠀⠀⣼⡿⠁⠀⠀⣰⠏⣠⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣧⣤⣴⡾⠋⠀⠀⠀⠀⠀⠀⠀⣃⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⡸⠀⠀⠀⠀⠀⠀⠀⣼⣿⣃⠤⠚⠚⠉⠉⠉⠙⠛
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⠉⠀⢀⡄⠀⠀⠀⠀⠀⠀⠙⢽⣿⠿⠋⠉⠁⠀⢠⡆⢰⠃⠀⠀⠀⠀⠀⠀⣼⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣴⡿⠁⠀⠀⠀⠀⠀⠀⠀⠈⢯⠀⠀⠀⠀⢀⡞⢠⠋⠀⠀⠀⠀⠀⢀⣾⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡄⠀⠀⠀⣸⢠⠃⠀⠀⠀⠀⠀⢠⣾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⡆⢠⠉⢿⣿⣿⡟⣿⣿⣿⣿⣿⣷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠳⡀⠀⠀⡇⠇⠀⠀⠀⠀⠀⣠⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣼⠀⠈⢿⣿⡇⢹⣿⣿⣿⣿⣿⣿⣿⡗⠤⣀⠀⠀⠀⠀⠀⠑⢄⣀⡞⠀⠀⠀⠀⢀⣴⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣷⠀⠀⠹⢇⠀⢻⣿⣿⣿⣿⣿⣿⣧⠀⠈⠻⣷⣦⣤⣀⡀⠀⠉⠀⠀⠀⣀⡴⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⠟⠀⠀⠀⠈⠳⣄⢻⣿⣿⣿⣿⣿⣿⣆⠀⠀⠈⠻⢿⣿⣿⣿⣷⣶⣴⣾⣿⣿⣿⣿⡿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣿⣿⣿⣄⠀⠀⠀⠀⠀⠈⠳⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⠉⡿⢿⣿⣿⣿⣿⣿⣿⣿⡿⢱⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "Confundida": r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣴⣶⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣤⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⡿⣻⣿⢛⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣼⣻⣿⣿⠟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠘⠿⣿⣿⣿⣲⣻⣿⣿⣿⣿⣿⣿⣿⣿⡷⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢹⣿⡟⠛⠛⠉⢈⠉⠙⠛⠛⣿⡷⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⢻⣷⡀⠀⠀⠤⠀⠀⢀⣼⣿⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣶⣤⣀⣠⣴⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⡟⣎⠉⠉⡜⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⣤⡤⠶⣾⣿⣿⣿⣄⣈⣦⣞⣀⣽⣿⣛⢧⣄⣀⠀⠀⠀⠀
⠀⠀⠀⣼⡏⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡌⠙⠛⠿⣿⡆⠀
⠀⠀⠀⢹⣷⠀⢀⣾⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣋⢡⡀⠀⢠⣾⠇⠀
⠀⠀⠀⢸⣿⣷⣾⡏⣿⡇⠛⡇⠉⣹⠀⢁⣿⢿⣿⣾⣧⣰⣿⡟⠀⠀
⠀⠀⠀⠈⣿⣿⣿⣷⣾⣿⣾⣷⡀⣿⡇⣼⣾⣿⣯⣤⣿⣿⣿⡇⠀⠀
⠀⠀⠀⠀⣿⡇⢻⣿⣿⣿⣿⣿⣿⣻⣿⣿⣿⣿⣿⣿⣿⡿⣿⠁⠀⠀
⠀⠀⠀⠀⢹⡉⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⢸⡇⠀⠀⠀
⠀⠀⠀⠀⠘⡇⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⡃⠀⡾⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢏⠀⠀⢻⡇⠙⠿⣿⣿⣿⡿⣿⡿⠁⠀⣠⠇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢸⡇⠀⠸⣿⠀⠀⠈⢩⣏⢀⡞⠁⠀⢀⡟⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣸⠇⠀⢠⣿⡄⠀⣤⣸⠋⢸⡀⠀⠀⢸⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣰⡿⡇⠰⠾⠋⡇⡈⠛⢻⠀⡷⠀⠀⢸⣯⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢰⣿⠁⢻⠀⠀⠀⣧⠀⢀⡿⣸⠇⠀⠀⣼⣿⣧⠀⠀⠀⠀⠀
⠀⠀⢠⣿⣿⣿⣺⡇⠀⠀⢹⡄⠀⣧⡿⠄⠀⢸⣟⢻⣿⡇⠀⠀⠀⠀
⠀⢠⡟⠁⠀⠈⢿⡇⠀⠀⢸⣇⠀⣿⠧⠀⢠⣿⡍⠉⠙⢸⡀⠀⠀⠀
⠀⣜⠄⠀⠀⠀⣸⣷⠀⠀⠰⣿⣴⡟⠁⠀⣾⡇⠀⠀⠀⠀⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "Asustada": r"""
⠀⠀⣠⣿⣿⠿⠿⠿⠷⠶⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⡶⠶⠿⠿⠿⢿⣿⣧⡀⠀⠀
⠲⣿⡟⠉⠀⠀⢀⣤⣶⣶⣶⣍⠛⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠟⢋⣴⣶⣶⣶⣄⠀⠀⠈⠙⣿⡷⠂
⠀⢹⡇⠀⠀⠀⠈⠈⢰⣤⣾⡟⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢽⣦⣴⠞⠙⠀⠀⠀⠀⣿⠃⠀
⠀⠀⢷⠀⠀⠀⠀⠘⠂⠉⠁⠠⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠣⠂⠉⠁⠀⠈⠀⠀⠀⢰⠃⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⢀⠀⢀⠔⢋⡠⢀⡀⠀⣀⠄⣀⠔⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⠀⠀⠀⠀⠀
⠀⢀⠔⢀⡤⠀⡠⠒⣀⠝⡡⠚⢁⠔⢋⠔⠉⡠⠞⡡⠞⠁⡠⠚⠀⣀⠄⠉⢁⠤⠊⠁⡠⠔⠉⠀⠀⠀
⠐⡡⠚⢁⠔⠉⡠⢊⠵⠊⡠⠖⡡⠚⢁⠤⢊⡠⠊⢀⠔⠊⢀⠴⠊⣠⠔⠊⢁⡤⠒⢉⠤⠂⠀⠀⠀⠀
⠈⠀⠞⠁⡴⠊⠀⠁⠠⠊⠔⠋⢀⠔⢁⠔⠉⣠⠾⣁⠀⠐⠁⠒⠉⠀⠤⠚⠁⠀⠊⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠁⢀⣌⣀⣀⣀⣡⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⠿⢿⣿⡿⠿⢿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠆⠀⠀⠀⠀⣂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⢄⠀⠀⠀⠀⠀⢀⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠃⠑⠀⠀⠀⠐⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "Aliviada": r"""
⠀⠀⠀⢀⡞⡥⠀⠀⠀⠀⣠⠴⢀⣡⠤⢦⡀⠀⠀⠀⠀⠀⠈⣆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢠⡞⢸⠁⠀⠀⣠⢚⡥⠚⠉⠀⠀⠘⣗⡄⠀⠀⢰⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢾⠇⡎⠀⠀⣰⡳⠋⠀⠀⣠⣤⠶⠢⡿⣸⣆⠀⠈⣧⣄⢸⠁⠀⠀⠀⠀⠀⠀
⠀⠀⢸⡄⢳⣠⣾⡟⠓⠆⠐⠘⠙⢀⣤⣶⢿⣤⣹⡅⠀⣿⠈⣿⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⡇⠸⡇⣾⡛⣶⡦⠀⠀⠀⠛⢱⢼⣷⠸⠋⢣⠀⡇⣹⠛⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢱⠀⠹⣏⠉⢟⣻⣀⠀⠀⠀⠐⠛⠛⠐⠀⠘⣴⡽⣇⠀⢸⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⢇⠀⠘⡄⠀⠀⢸⡁⠀⠀⠀⠀⠀⠀⠀⠀⣿⢠⢹⡀⠈⣧⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⢦⠀⢻⢦⡀⠈⠰⣶⠖⠂⠀⠀⢀⡤⠀⡇⢘⡆⢇⠀⠸⣷⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠳⡼⡀⣟⡶⢄⡀⠀⢀⡠⠖⠁⠀⢀⡇⢸⢻⠸⡀⠀⣿⢇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢠⠏⢳⠟⢀⠷⠈⣹⡇⠀⠀⠀⠀⣼⢣⡞⢸⠀⡇⢰⣼⢸⠀⠀⠀
⠀⠀⠀⠀⠀⢀⠎⣠⠋⢀⡼⠟⠊⠟⠀⠀⠀⠀⠀⣿⠀⠑⢯⣀⣇⣎⢏⡞⠀⠀⠀
⠀⠀⠀⢀⡠⠾⠔⠓⢞⣁⣀⣀⠀⠀⠀⠀⠀⠀⠀⢻⣀⣀⣀⣈⡛⡿⡯⡀⠀⠀⠀
⠀⠀⢠⠋⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠐⠉⠉⠉⠉⠉⣧⡀⠀⠀⠐⠑⢧⠁⠀⠀⠀
⠀⠀⢻⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠧⠀⠀⠀⠀⠀⠀⢗⠀⠀
⠀⠀⢸⠀⠀⡼⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⠀⠀⠀⠀⠀⢈⡆⠀
⠀⠀⠘⡤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⡀⠀⠀⠀⠀⢠⠁⠀
⠀⣠⠎⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢣⠀⠀⠀⠀⡎⠀⠀
⢠⠇  ⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠘⡄⠀⠀⡸⠀⠀⠀
⢸⡀   ⠀⠀⠀⠀⠀⠀⠀⣸⠀⠀⠀⠀⠀⠀⠀  ⠀⠀⡇⠀⢀⠇⠀⠀⠀
⠀⢷⡀⠀ ⠀⠀⠀⠀⠀⠀⠀⠸⡀⠀⠀⠀⠀⠀ ⠀⠀⠀⣴⠁⠀⠀⡃⠀⠀⠀
⠀⠀⠑⢤⣀⠀⠀⢀⣠⠴⠋⠀⠀⠙⢦⡀⠀⠀⠀⠀⠀⣀⡴⠁⠀⢠⠃⠀⠀⠀⠀
⠀⠀⠀⠀⢠⢻⠉⠁⠀⠀⠀⠀⠀⠀⠀⠈⠉⠒⠒⠒⠉⡽⠀⠀⠀⡼⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠸⣾⠀⠐⠀⠀⠀⠀⠀⠑⢤⡀⠀⠀⠀⠀⠀⡇⠀⠀⢠⠇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣿⡄⠀⠀⢠⡀⠀⠀⠀⠀⠙⣄⠀⠀⠀⢰⠁⠀⠀⣼⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢿⣇⠀⠀⢸⠀⠀⠀⠀⠀⠀⠈⠁⠀⢀⡜⠀⠀⠀⡗⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "Agradecida": r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⢀⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠐⠀⣴⣤⡀⠀⢀⣀⣤⠤⠤⠶⠖⠒⠒⠒⠒⠒⠲⠶⠤⢤⣀⡀⣼⣛⣧⠀⢁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣸⣏⢻⣍⠁⠀⢀⡀⠤⠄⠒⠒⠒⠒⠒⠒⠀⠤⠄⠀⠀⢸⡳⢾⢹⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣠⠖⠋⠀⢯⡞⣎⡆⠁⠀⠀⠀⢀⡀⠀⠤⠤⠤⠤⠄⠀⡀⠀⠀⠻⣽⣻⡌⠹⣄⠀⠐⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⡾⠁⠀⠀⢀⢾⣹⢿⣸⠀⣰⠎⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠆⠹⡿⣏⢆⠈⢷⡀⠀⠆⠀⠀
⠀⠀⠀⠀⣰⠏⠀⠀⢀⠔⠛⠄⠙⠫⠇⢀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢄⠠⠒⠒⠵⡈⢳⡀⠀⠀⠀
⠀⠄⠀⡰⠁⠀⠀⢠⠊⠄⠂⠁⠈⠁⠒⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⡀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠄⢳⡀⠈⠀
⠈⠀⣸⠃⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠀⠀⠐⠀⠀⠐⠀⢀⠀⠀⠀⠀⢷⠀⠀
⠀⢠⠇⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠀⠀⠀⠀⠀⠰⠀⠀⠀⠀⠀⠀⡄⠀⡀⠆⢰⠀⠀⠀⡄⠀⠀⠀⠸⡄⠀
⠀⣼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠉⠀⡄⠀⢀⠀⠀⡄⠂⠆⠀⠀⠀⠀⢁⠀⢁⠀⢸⠀⢇⠀⡇⠀⠀⠀⠀⣧⠀
⠀⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠰⡃⠄⠈⡄⠀⡇⢀⢰⠀⠀⠀⠀⡼⠀⠸⢰⠀⣤⣅⣁⣴⠀⠀⠀⠀⢻⠀
⢠⡇⠀⠀⠀⠀⠀⠀⠀⠠⠀⠀⠀⠱⢀⣁⣤⣧⣴⣧⣄⡇⢸⣸⡄⠀⢀⣆⠀⣦⠊⢹⣿⣿⡛⠻⢿⠀⠀⠀⠀⢸⡇
⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⣃⠀⠀⢴⣿⠟⠉⢈⣿⣿⣿⡟⠇⠀⠀⠀⠀⠀⠀⢸⣶⣿⣿⡿⣧⠀⢸⡇⠀⢃⠀⢸⡇
⠈⡇⠀⠀⠀⠀⠀⠀⠀⡀⢉⡄⠀⢸⠁⠀⣷⣾⣿⣿⡟⣿⠀⠀⠀⠀⠀⠀⠀⠀⢧⠙⠋⢁⡟⢀⡦⢧⠀⠸⡇⢸⡇
⠀⣿⠀⠀⠀⠀⠀⠀⢀⠔⠪⡄⠀⠸⣁⠀⠹⣉⠉⠉⢠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠈⠓⢲⠛⠆⢉⠀⢸⠀⢀⢇⢸⡇
⠀⢿⠀⠀⠀⠀⠀⢀⠃⡐⠐⣴⠀⠀⠏⠉⠖⠉⠋⡙⠁⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⢀⡠⠀⠊⠄⠌⢘⠀⠀⠸⢸⠀
⠀⢸⠀⠀⠀⠀⠀⠈⣆⢃⠘⠘⡀⠀⡸⡘⡐⡐⠠⠁⠀⡴⡖⣲⠒⠊⠉⠉⠉⠙⢿⣤⡇⠀⠀⠀⠈⢐⠀⠀⠁⣿⠀
⠀⠘⡇⠀⠀⠀⠀⠀⠈⢶⠬⣁⡇⠀⠀⠑⠐⠤⠐⠀⠀⡇⠉⠀⠀⠀⠀⠀⠀⠀⠀⢙⠇⠀⠀⠀⠀⣼⢀⠀⠀⣿⠀
⠀⠀⣇⠀⠀⠀⢰⠀⠀⠈⠀⠂⡇⠀⠃⢡⠀⠀⠀⠀⠀⠹⡄⠀⠀⠀⠀⠀⠀⠀⣠⠎⠀⠀⢀⡴⡞⡉⠈⠀⠀⣿⠀
⠀⠀⣹⠀⠀⠀⠀⠀⠀⠀⠀⡀⡇⠀⢰⠈⡷⡀⠀⠀⠀⠀⠸⢶⣀⠀⠀⢀⣰⠎⠁⢀⡶⠏⠁⣈⠆⠁⡀⠰⢸⡇⠀
⠀⠀⢸⡀⢸⠀⠀⠆⠀⠀⠀⠀⡇⠀⠀⠀⢡⡄⡏⢆⠒⠢⠤⠤⠤⢨⠥⡴⠒⠚⠉⠉⠀⠀⡠⠁⡘⢠⠁⢀⠆⡇⠀
⠀⠀⢸⡇⠀⡀⠀⠀⠀⠀⢠⢠⠁⠀⠘⡀⠠⣷⠃⠀⠀⠀⠀⠉⢰⠈⢱⠄⡀⡄⠀⢸⠀⠐⠀⠰⠁⠀⠀⡞⠄⣷⠀
⠀⠀⠀⣷⠀⡇⠀⠀⠀⠸⠀⡈⠀⠀⢂⠃⠀⡄⠇⠀⠀⠀⠀⠀⢔⠳⠀⠀⠣⠍⠒⠤⣰⠁⢠⠃⢠⠀⠀⠅⠀⢻⡀
⠀⠀⠀⠉⠀⠁⠀⠀⠀⠀⠀⠁⠀⠀⠈⠀⠀⠁⠈⠀⠀⠀⠀⠀⠀⠉⠁⠀⠀⠈⠁⠀⠈⠀⠁⠀⠈⠀⠀⠁⠀⠈⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "Frustrada": r"""
⠀⠀⠀⠀⢀⡠⠤⠔⢲⢶⡖⠒⠤⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣠⡚⠁⢀⠀⠀⢄⢻⣿⠀⠀⠀⡙⣷⢤⡀⠀⠀⠀⠀⠀⠀
⠀⡜⢱⣇⠀⣧⢣⡀⠀⡀⢻⡇⠀⡄⢰⣿⣷⡌⣢⡀⠀⠀⠀⠀
⠸⡇⡎⡿⣆⠹⣷⡹⣄⠙⣽⣿⢸⣧⣼⣿⣿⣿⣶⣼⣆⠀⠀⠀
⣷⡇⣷⡇⢹⢳⡽⣿⡽⣷⡜⣿⣾⢸⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀
⣿⡇⡿⣿⠀⠣⠹⣾⣿⣮⠿⣞⣿⢸⣿⣛⢿⣿⡟⠯⠉⠙⠛⠓
⣿⣇⣷⠙⡇⠀⠁⠀⠉⣽⣷⣾⢿⢸⣿⠀⢸⣿⢿⠀⠀⠀⠀⠀
⡟⢿⣿⣷⣾⣆⠀⠀⠘⠘⠿⠛⢸⣼⣿⢖⣼⣿⠘⡆⠀⠀⠀⠀
⠃⢸⣿⣿⡘⠋⠀⠀⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⡆⠇⠀⠀⠀⠀
⠀⢸⡿⣿⣇⠀⠈⠀⠤⠀⠀⢀⣿⣿⣿⣿⣿⣿⣧⢸⠀⠀⠀⠀
⠀⠈⡇⣿⣿⣷⣤⣀⠀⣀⠔⠋⣿⣿⣿⣿⣿⡟⣿⡞⡄⠀⠀⠀
⠀⠀⢿⢸⣿⣿⣿⣿⣿⡇⠀⢠⣿⡏⢿⣿⣿⡇⢸⣇⠇⠀⠀⠀
⠀⠀⢸⡏⣿⣿⣿⠟⠋⣀⠠⣾⣿⠡⠀⢉⢟⠷⢼⣿⣿⠀⠀⠀
⠀⠀⠈⣷⡏⡱⠁⠀⠊⠀⠀⣿⣏⣀⡠⢣⠃⠀⠀⢹⣿⡄⠀⠀
⠀⠀⠘⢼⣿⠀⢠⣤⣀⠉⣹⡿⠀⠁⠀⡸⠀⠀⠀⠈⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "Orgullosa": r"""
⠀⠀⠀⣿⡇⡘⣾⣿⣿⡇⣸⡯⠽⠟⢋⣉⠑⡞⠀⡼⢠⢧⠀⠀⡇⠈⢿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠐⡿⢰⢁⡟⠀⠉⣰⠙⡿⣷⣶⢦⡄⢰⠁⢰⠃⣸⡌⠀⢸⠃⢀⢾⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣷⢸⢸⢧⡰⢼⣿⡀⠉⠀⠈⠀⠀⠀⢧⢇⣸⣳⠁⡰⢃⠀⣸⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢿⣿⡸⣼⡝⢦⠣⠁⠀⠀⠀⠀⠀⠀⠘⠙⠻⢥⠞⢁⠜⣰⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⢿⢿⣼⣇⠘⣧⡀⠀⠀⠀⠀⠀⠄⠀⠀⠀⠀⣼⣧⣾⡷⠛⢿⠓⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠸⠺⣿⣿⣇⣿⠙⢦⡀⠀⠀⠀⠀⠀⠀⢀⣼⡿⠋⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢀⡤⠶⠶⠿⢿⣿⡇⠀⠀⠈⠓⠤⣤⡤⠖⠊⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⡴⠋⠀⠀⠀⠀⠀⠙⠓⠤⠄⣀⡀⠀⢸⣷⣦⡤⠤⠖⠒⠒⠢⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢸⠃⠀⠀⠀⠀⠀⢀⢆⡀⠀⠂⠒⠒⠒⠻⠦⣄⡀⠀⢀⠢⠤⠤⢄⡹⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡚⠀⠀⠀⠀⠀⠀⡸⠋⠀⠀⠀⠀⠀ ⠀⠀⠀⠈⠳⡄⠀⠀⠀⠀⠀⠈⠉⠳⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀
⢹⠀⠀⠀⠀⠀⢠⠇⠀⠀⠀⠀⠀⠀  ⠀⠀⠀⠀⠙⡄⠀⠀⠀⠀⠀⠀⠀⢬⣱⣄⠀⠀⠀⠀⠀⠀⠀
⠀⣇⠀⠀⠀⠀⢸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠻⡄⠀⠀⠀⠀⢇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⡿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣷⠀⠀⠀⠀⠈⡦⣀⠀⠀⠀⠀⠀⠀⠀⣀⠠⠖⠋⠈⠳⣄⠀⠀⠀⠀⠀⠀⢠⡟⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠹⡄⠀⠀⠀⠀⢸⠈⠉⠒⠒⠒⠊⠉⠁⠀⠀⠀⠀⠀⠀⠈⠳⣆⡀⠀⢀⡴⠟⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢥⠀⠀⠀⠀⢸⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⡿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⡄⠀⠀⠀⢸⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⣷⠀⠀⠀⠀⡹⣿⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠀⠀⠛⢧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣿⠄⠀⠀⠀⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠭⠄⠀⠀⡰⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⡄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠸⡆⠀⢰⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠓⢄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢻⣄⡎⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠢⡱⡄⠀⠀⠀
⠀⠀⠀⠀⠀⠈⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠁⠙⡄⠀⠀
⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠃⠀⠀⠀⠀⠹⡄⠀
⠀⠀⠀⠀⢀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠏⠀⠀⠀⠀⠀⠀⠹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "Esperanzada": r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⢔⣦⣶⣿⣿⣿⣿⡷⠖⠒⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠉⠁⠂⠀⠀⢀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣰⠶⣦⡤⣄⠀⠀⠀⠀⠀⠀⣠⠖⢩⣶⣿⣿⣿⣿⣿⠟⢉⣠⠔⠊⠁⠀⠀⠀⣀⣄⠀⠀⠉⠑⢦⣠⣤⣤⡀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠘⢷⣌⡧⡾⠀⠀⠀⠀⡠⠊⢁⣴⣿⣿⣿⣿⣿⢟⣠⡾⠟⠁⠀⣀⣤⣶⠞⣫⠟⠁⠀⢀⠄⠀⢀⠙⢿⣿⣿⣷⣄
⠀⠀⠀⠀⢠⠀⠀⠀⠀⠀⠉⠉⠁⠀⠀⣠⣾⣶⣶⣿⣿⣿⣿⣿⣿⣷⡿⠋⣀⣤⣶⣿⣿⣋⣴⡞⠁⠀⠀⣠⠊⠀⠀⢸⡄⢨⣿⣿⣿⣿
⠀⠀⠀⠀⠀⢃⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⠿⠿⢻⣿⣿⣿⣿⣿⣿⠿⠛⢉⣴⣿⢿⣿⠏⠀⠀⠀⡴⠃⣰⢀⠀⢸⣿⣤⣏⢻⣿⣿
⠀⠀⠀⠀⠀⠘⡆⠀⠀⠀⠀⠀⢀⣾⡿⣿⡿⠁⠀⢀⣾⣿⣿⣿⡿⠋⠁⠀⣠⣿⠟⢡⣿⡟⠀⢀⣤⣾⠁⣼⣿⢸⡇⢸⣿⣿⣿⡈⣿⣿
⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⢀⣾⠋⣼⣿⠁⢀⠀⣼⣿⣿⠟⠁⠀⠀⠀⣰⡿⠋⢠⣿⡿⠁⢠⣾⣿⡏⢀⣿⣿⣾⣿⢸⣿⣿⣿⡇⢹⣿
⠀⠀⠀⢰⡶⣤⣤⣄⠀⠀⠀⡼⠁⣼⣿⣿⣾⣿⣰⣿⠟⠁⠀⠀⠀⠀⢠⡿⠁⠀⣾⣿⠃⢠⣿⢿⡿⠁⠸⢿⣿⣿⣿⣿⣿⣿⣿⣿⠸⣿
⠀⠀⠀⠘⣧⣈⣷⡟⠀⠀⣰⠁⡼⢻⣿⣿⣿⣿⡿⠋⠀⠀⠂⠒⠒⠒⣾⠋⠀⢠⣿⡏⢠⣿⢃⡿⠁⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⠀⣿
⠀⠀⠀⠀⠈⠉⠁⠀⠀⢠⠇⣰⠁⠸⣹⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⠐⡇⠀⠀⢸⣿⢃⣿⠋⣿⡀⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⠀⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣰⠃⡀⢀⣿⣿⡏⢘⣶⣶⣶⣷⣒⣄⠀⠀⠀⠀⠀⠸⣿⣾⠃⠰⠁⠙⢦⡀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⢠⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡔⢁⠞⢁⣾⣿⣿⣷⠟⠁⣠⣾⣿⣿⣧⠀⠀⠀⠀⠀⠀⣿⡏⠀⠀⠀⠀⠀⠙⢦⡀⠀⢿⣿⣿⣿⣿⣿⣿⣸⠃
⠀⠀⠀⠀⠀⠀⠀⣠⣾⡖⠁⣠⣾⣿⣿⣿⡏⠀⢰⠿⢿⣿⣯⣼⠁⠀⠀⠀⠀⠀⠹⠀⠀⠀⠀⠀⠀⠀⠀⠈⠢⢬⣿⣿⡘⣿⣿⣏⣿⠀
⠀⠀⠀⠀⠀⣠⣾⢟⠋⣠⣾⣿⡿⠋⢿⣿⠀⠀⢼⠀⠀⢀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣙⣷⣴⣆⡀⠀⠀⠈⢿⣧⠸⣿⣿⣿⣿
⠀⠀⢀⡤⠞⢋⣴⣯⣾⡿⠟⠋⠀⠀⢸⣿⡆⠀⠸⡀⠉⢉⡼⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣿⣶⣆⠀⠈⢿⣧⠹⣿⣿⣿
⠀⠀⠀⣸⣶⣿⣿⠟⠋⠀⠀⠀⠀⣴⡎⠈⠻⡀⠈⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠿⠛⠛⠻⣿⣬⡏⠻⣷⡀⠈⢻⣿⣿⣿⣿
⢂⣠⣴⣿⡿⢋⣼⣿⣿⣿⣿⣿⠋⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠺⡄⠀⠀⢀⡾⣿⠁⠀⢹⡇⠀⢠⣿⣿⣿⣿
⣿⣿⣽⣯⣴⣿⣿⠿⡿⠟⠛⢻⡤⠚⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡇⠈⠉⢉⡴⠃⠀⠀⢸⠇⢠⣿⣿⣿⣿⣿
⣿⡇⣿⠿⣯⡀⠀⠀⠈⣦⡴⠋⠀⠀⢀⠨⠓⠤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠷⠒⠋⠀⠀⠀⠀⠃⣴⣿⠿⣡⣿⠏⠀
⠁⠀⠃⠀⠈⠳⣤⠴⡻⠋⠀⢀⡠⠊⠁⠀⠀⢀⡽⢄⠀⠘⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣾⣿⠏⣺⠟⠁⠀⠀
⠀⠀⠀⠀⠀⡰⠋⢰⠁⠀⠀⠀⠀⠀⣀⠤⠊⠁⠀⠀⢱⡀⠘⢆⡀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠖⠛⠛⢉⣤⠞⠁⠀⠀⠀⠀
⠀⠀⠀⠀⡜⠁⠀⠈⢢⡀⠀⠀⠀⠀⠁⠀⠀⠀⣀⠔⠋⢱⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡞⠉⠀⠀⠀⣀⠀⠀⠈
⠀⠀⠀⡜⠀⠀⠀⠀⢰⠑⢄⠀⠀⠀⠀⠀⠀⠊⠀⢀⣀⢀⠇⠀⡠⠒⠒⢶⠈⠉⠑⡖⠈⠓⢢⠤⢄⣀⣴⣾⣏⠉⠛⠋⠉⠉⠀⠀⠀⢠
⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠑⣄⡀⠀⠀⠀⠀⠀⠀⣹⡿⢤⣼⠃⠀⠀⢸⠀⠀⠀⡇⠀⠀⢸⠀⠀⠈⣿⣿⣿⣦⣀⣀⣀⣀⣀⣶⢶⣿
⠀⠀⠀⠀⠀⣠⠔⠒⢻⠀⠀⠀⠃⠉⠒⠤⣀⡀⠤⠚⠁⣇⡰⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠌⠀⠀⣰⠟⠋⠁⠀⠀⠀⠀⠈⠉⠛⠦⡻⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "Cansada": r"""
⠀⠀⠀⣿⡇⡘⣾⣿⣿⡇⣸⡯⠽⠟⢋⣉⠑⡞⠀⡼⢠⢧⠀⠀⡇⠈⢿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠐⡿⢰⢁⡟⠀⠉⣰⠙⡿⣷⣶⢦⡄⢰⠁⢰⠃⣸⡌⠀⢸⠃⢀⢾⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣷⢸⢸⢧⡰⢼⣿⡀⠉⠀⠈⠀⠀⠀⢧⢇⣸⣳⠁⡰⢃⠀⣸⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢿⣿⡸⣼⡝⢦⠣⠁⠀⠀⠀⠀⠀⠀⠘⠙⠻⢥⠞⢁⠜⣰⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⢿⢿⣼⣇⠘⣧⡀⠀⠀⠀⠀⠀⠄⠀⠀⠀⠀⣼⣧⣾⡷⠛⢿⠓⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠸⠺⣿⣿⣇⣿⠙⢦⡀⠀⠀⠀⠀⠀⠀⢀⣼⡿⠋⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢀⡤⠶⠶⠿⢿⣿⡇⠀⠀⠈⠓⠤⣤⡤⠖⠊⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⡴⠋⠀⠀⠀⠀⠀⠙⠓⠤⠄⣀⡀⠀⢸⣷⣦⡤⠤⠖⠒⠒⠢⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢸⠃⠀⠀⠀⠀⠀⢀⢆⡀⠀⠂⠒⠒⠒⠻⠦⣄⡀⠀⢀⠢⠤⠤⢄⡹⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡚⠀⠀⠀⠀⠀⠀⡸⠋⠀⠀⠀⠀⠀ ⠀⠀⠀⠈⠳⡄⠀⠀⠀⠀⠀⠈⠉⠳⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀
⢹⠀⠀⠀⠀⠀⢠⠇⠀⠀⠀⠀⠀⠀  ⠀⠀⠀⠀⠙⡄⠀⠀⠀⠀⠀⠀⠀⢬⣱⣄⠀⠀⠀⠀⠀⠀⠀
⠀⣇⠀⠀⠀⠀⢸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠻⡄⠀⠀⠀⠀⢇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⡿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣷⠀⠀⠀⠀⠈⡦⣀⠀⠀⠀⠀⠀⠀⠀⣀⠠⠖⠋⠈⠳⣄⠀⠀⠀⠀⠀⠀⢠⡟⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠹⡄⠀⠀⠀⠀⢸⠈⠉⠒⠒⠒⠊⠉⠁⠀⠀⠀⠀⠀⠀⠈⠳⣆⡀⠀⢀⡴⠟⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢥⠀⠀⠀⠀⢸⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⡿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢸⡄⠀⠀⠀⢸⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⣷⠀⠀⠀⠀⡹⣿⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠀⠀⠛⢧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣿⠄⠀⠀⠀⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠭⠄⠀⠀⡰⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⡄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠸⡆⠀⢰⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠓⢄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢻⣄⡎⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠢⡱⡄⠀⠀⠀
⠀⠀⠀⠀⠀⠈⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠁⠙⡄⠀⠀
⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠃⠀⠀⠀⠀⠹⡄⠀
⠀⠀⠀⠀⢀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠏⠀⠀⠀⠀⠀⠀⠹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "Nostálgica": r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠤⠤⠠⡖⠲⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠐⠀⠀⠀
⠀⠀⠀⠀⠀⡠⠶⣴⣶⣄⠀⠀⠀⢀⣴⣞⣼⣴⣖⣶⣾⡷⣶⣿⣿⣷⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄⠀⠉⠀⠀⠀⠀
⠀⠀⠀⠀⢸⠀⠀⠀⠙⢟⠛⠴⣶⣿⣿⠟⠙⣍⠑⢌⠙⢵⣝⢿⣽⡮⣎⢿⡦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄⠀⠀⠂⠁⠀⠀⠀⠀
⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⢱⡶⣋⠿⣽⣸⡀⠘⣎⢢⡰⣷⢿⣣⠹⣿⢸⣿⢿⠿⡦⣄⠀⠀⠀⠀⠀⠀⡠⠀⠀⠂⠂⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⢧⡿⣇⡅⣿⣇⠗⢤⣸⣿⢳⣹⡀⠳⣷⣻⣼⢿⣯⡷⣿⣁⠒⠠⢄⡀⠀⠀⡀⠀⠁⠄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⣼⣿⣧⡏⣿⣿⢾⣯⡠⣾⣸⣿⡿⣦⣙⣿⢹⡇⣿⣷⣝⠿⣅⣂⡀⠀⠡⢂⠄⣈⠀⠄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠇⠀⠀⠀⠀⣿⡟⣿⡇⡏⣿⣽⣿⣧⢻⡗⡇⣇⣤⣿⣿⣿⣧⣿⣿⡲⣭⣀⡭⠛⠁⠀⠀⣨⠁⠉⣂⢄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠸⠀⠀⠀⠀⢻⣿⣇⣥⣏⣘⣿⣏⠛⠻⣷⠿⡻⡛⠷⡽⡿⣿⣿⣿⣷⠟⠓⠉⠢⢄⡀⢠⠇⠀⠀⠀⠁⠫⢢⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢇⠀⠀⠀⢸⣾⣿⣽⣿⣏⣻⠻⠁⢠⠁⠀⠀⠀⠘⣰⣿⣿⢟⢹⢻⠀⠀⠀⠀⠀⠈⡒⢄⡀⠀⠀⠀⠀⠀⠀⠑⢄
⠀⠀⠀⠀⠀⠀⠘⡄⠀⠀⢸⣯⣿⣿⣿⢷⡀⠀⠀⠀⠀⠀⠀⠀⠛⣩⣿⣿⢿⣾⣸⠀⠀⠀⠀⠀⠀⣅⡠⠚⠉⠉⠁⠀⠀⠀⢀⠌
⠀⠀⠀⠀⠀⠀⠀⢡⠀⠀⠀⢟⣿⣯⡟⠿⡟⢇⡀⠀⠀⠐⠁⢀⢴⠋⡼⢣⣿⣻⡏⠀⠀⠀⣀⠄⠂⠁⠀⠀⠀⠀⠀⠀⢀⡤⠂⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠇⠀⠀⠈⠊⢻⣿⣜⡹⡀⠈⠱⠂⠤⠔⠡⢶⣽⡷⢟⡿⠕⠒⠀⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⡠⠐⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠘⡄⠀⠀⠀⠀⢿⠿⠿⢿⠾⣽⡀⠀⠀⠀⠈⠻⣥⣃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⠒⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⡀⡀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣖⠂⠠⠐⠋⠀⠙⠳⣤⣠⠀⠀⠀⣀⠤⠒⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠵⡐⠄⠀⠀⠀⠀⠀⠀⠀⠈⢷⣄⡀⠀⠠⡀⠀⠈⠙⠶⣖⡉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡥⠈⠂⠀⠀⠀⠀⠀⠀⠀⣼⠉⠙⠲⣄⠈⠣⡀⠀⠀⠈⢻⡦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡄⠀⠀⠀⠀⠀⠀⠀⢠⠇⠀⠀⠀⠈⣷⡄⠈⠄⠀⠀⠀⢧⠀⠑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡄⠀⠀⠀⡀⠀⢠⣿⣤⣤⣶⣶⣾⣿⣿⡄⢸⠀⠀⠀⢸⣄⣤⣼⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡄⠀⠀⠇⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⢸⠀⠀⠀⣼⣿⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣀⣀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⢀⣼⣿⣿⣿⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠉⠁⠀⠈⠉⠙⠛⠿⠿⠽⠿⠟⠛⡉⠛⠲⣿⣿⠿⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡇⠀⠀⢠⡏⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠋⠀⠀⣠⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢔⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "Emocionada": r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⣤⣄⣠⡾⠋⠁⠀⣀⡀⠀⠀⢀⣴⡶⠀⡀⣠⡆⠀⠀⠀⢀⠀⠀⠀⠀⠀⠙⠷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡴⠞⠋⠁⠀⣰⡾⢋⡀⠀⠀⣰⡟⠀⠀⣤⣿⡿⠁⢈⣶⠏⢻⡌⠐⠁⢸⣆⠀⠀⠀⠀⠀⠀⠈⠳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⠋⠀⠀⠀⠀⣼⠟⢠⡿⠇⠂⣴⡟⣀⣀⡾⢋⣾⠁⣠⡿⠁⠀⠈⢷⡐⢂⢸⡿⣆⠀⠀⢿⡄⠀⠀⠀⠙⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣠⡞⠃⠀⠀⠀⠀⠀⣼⠏⢠⡿⢁⣤⣶⣿⢟⣻⠟⠙⣻⣿⣾⠏⠀⠀⠀⠀⠈⣷⣘⣘⣧⠹⣖⠀⠸⣷⠀⠀⠀⠀⠸⣆⣠⣤⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⡼⠋⠀⠀⠀⠀⠀⠀⣼⠏⢀⣿⡃⠛⣽⢿⣯⣿⣿⣶⣦⣿⣾⠋⠀⠀⠀⠀⠀⠀⠘⢿⡻⣿⠛⠻⣷⣤⣿⡄⠀⢀⡀⠀⢹⡇⠀⠀⠈⠙⠳⣦⡀⠀⠀⠀⠀⠀
⠀⠀⠀⢠⡞⠁⠀⠀⠀⠀⠀⠀⣸⡿⣸⣿⡿⠂⣾⣯⣾⣿⡷⠋⠙⣿⣿⣿⡦⠀⠀⠀⠀⠀⠀⣀⣼⣷⣿⣦⣤⣹⣏⢻⣷⣤⢈⣿⠀⠈⣿⠀⠀⠀⠀⠀⠈⢳⣄⠀⠀⠀⠀
⠀⠀⢠⡟⠀⠀⠀⠀⠁⠀⠀⠀⣿⣿⡿⢻⣇⣾⢳⡟⠀⣾⣿⣦⣴⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⣻⠟⠉⢻⣿⣿⣿⢿⣾⡿⣿⢿⣿⡆⠄⣿⡂⠀⠀⠀⠀⠀⠀⠹⣆⠀⠀⠀
⠀⢀⡿⠀⠀⡀⠀⠀⠀⠀⠀⢈⣿⣿⣵⢻⣿⠇⣿⠀⢸⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⢀⣿⣧⣤⣼⣿⣿⣿⡇⠿⣧⢻⣄⣿⡇⠀⣿⠇⢈⠀⠀⠀⠀⠀⠀⢹⡆⠀⠀
⠀⣾⠁⠀⠁⠀⠀⠀⢀⣠⠾⠋⠀⣿⠿⠸⣿⠀⣿⠀⢸⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⡇⠀⢻⡈⣿⣿⠷⣤⣿⠁⠀⠀⠀⠁⠂⠀⠀⠀⢿⠀⠀
⢠⡇⠀⠀⢀⣠⡴⠞⠋⠁⠀⠀⠀⢹⡀⢀⡇⠀⠀⠀⠈⢻⣿⣿⣿⣿⡿⠃⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⡇⠀⣸⠇⢸⣿⣤⠘⡟⣧⠀⠀⠀⠀⠀⠀⠀⠀⠘⡇⠀
⠈⠛⠖⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠻⣼⠃⠀⠀⠀⠀⠀⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⣿⣿⠟⠀⠰⠟⠀⣠⢻⢼⢡⠇⠘⢧⡀⠀⠀⠀⠂⠀⠀⠀⢿⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠛⠋⠁⠀⠀⠀⠀⢠⣏⡟⠀⡾⠀⠀⠈⢳⣄⠀⠀⠀⠀⠀⠀⢸⡄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡖⠲⠶⠤⠤⠤⢤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⣠⡾⠁⠀⠀⠀⠀⠙⢷⡄⠀⠀⠀⠀⢸⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢧⡀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡞⠓⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣄⠀⠀⠀⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠷⣄⡀⠀⠀⠀⠀⠸⣇⠀⠀⠀⠀⢠⡟⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠳⢦⣸⠇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠶⣤⣀⠀⠀⠙⠳⠦⡤⠶⠋⠀⠀⠀⠀⠀⢀⣠⠶⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠓⠶⣤⠄⢠⣤⣀⣤⣤⠤⠶⠚⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡖⢻⡇⠀⣼⠷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⡛⣿⣿⣟⣿⣷⣾⠿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⢻⡇⠈⢻⣿⣟⠉⠁⣲⠸⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡷⣿⠀⠀⢸⣿⠃⠀⠀⢺⠶⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⢿⡏⠀⠀⢸⢿⡆⠐⠀⢸⣿⢿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡟⣾⠃⠀⠀⠻⠘⠇⠀⠀⢸⢻⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⠑⣿⣿⣶⣤⣶⣶⣶⣶⣶⡞⢸⡞⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠷⠴⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⢸⣀⡼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "Aburrida": r"""
⠀⠀⠀⠀⠀⠀⢀⠞⡰⠁⠀⡼⠀⠀⠀⣰⠇⣸⡇⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠀⡄⣂⠀⢞⡤⡄⠀⣧⠀⠠⡄⠀⠀⠘⡞⠿⠹⣞⢮⠻⡝⢦⠀⠀⠀⠀⠀⠀
⠀⢤⣀⣼⣁⣀⡞⡸⠁⠀⢰⠃⠀⠀⠀⠛⢀⠟⠁⠀⠀⢸⡇⠀⠀⠀⣸⠀⠀⠀⠀⢸⢸⠻⠀⠈⠃⡇⠀⢸⠀⠀⢧⠀⠀⠀⢹⡀⠀⠁⠀⢣⡹⡌⠳⡀⠀⠀⠀⠀
⠞⠉⠀⣐⠆⠈⠑⠣⡄⠀⡞⠀⠀⠀⠀⠀⣸⠀⠀⠀⠀⣸⠀⠀⠀⠀⡇⠀⠀⠀⠀⢸⠨⠀⠀⠀⠀⢳⠀⢸⡆⠀⢸⠀⠀⠀⠀⡇⠀⠀⠀⠀⢱⡹⡄⠙⣅⠀⠀⠀
⠀⠀⠈⠀⠀⠀⠈⠂⡇⢰⠃⠀⠀⠀⠀⠀⡏⠀⠀⠀⢠⣿⠀⠀⠀⢰⡇⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⢸⠀⢸⢧⠀⠘⡇⠀⠀⠀⢸⠀⠀⢦⠀⠀⢣⢱⠀⠙⡆⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡧⡾⠀⠀⠀⠀⠀⠀⡇⠀⠰⢤⣸⡇⠀⠀⠀⡾⢳⠀⠀⠀⠀⠘⡆⠀⠀⠀⠀⢸⠀⢸⢸⠀⠀⣿⣠⠄⠀⢸⠀⠀⢸⠀⠀⡌⡎⣇⡁⠹⡄⠀
⠀⠀⠀⠀⠀⠀⠀⢠⠃⡇⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⡇⡏⠓⠲⢤⣇⣸⡀⠀⠀⠀⠀⡇⠀⠀⠀⠀⡼⣀⣾⣼⡖⠋⡏⡇⠀⠀⢸⠀⠀⠈⡇⠀⢹⣹⢸⢣⠀⢳⠀
⣻⠗⠲⢶⣒⡒⠲⡏⢹⠁⠀⠀⠀⠀⠀⠀⣇⠀⠀⢰⠃⢹⠀⠤⢼⠓⠛⣯⠍⠃⠀⠀⢻⡆⠀⠐⡾⡟⢻⠗⠚⡇⢠⠇⢹⠀⠀⢸⠀⠀⠀⣷⠀⢸⡏⡎⣟⠀⠈⠃
⠀⠠⠚⠁⠀⠈⡇⢱⣼⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⢸⣠⣼⣒⠾⢽⣒⡲⢼⡄⠀⠀⠀⠸⡇⠀⠀⣸⡵⣞⡭⠬⣯⣺⠤⠘⡄⠀⢸⠀⠀⢀⢹⠀⢸⢸⠇⡇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠁⢸⡽⠀⠀⠀⠀⠀⠀⠀⡟⡆⣠⢿⣋⢭⣷⠖⢾⣦⣝⣷⠽⡄⠀⠀⠀⣇⠀⢀⣿⣿⣵⣶⡶⡷⣾⡙⢆⡇⠀⣿⡇⠀⢸⢸⠀⣸⠘⡄⣿⠀⠀⠀
⠀⠀⠀⠀⢀⣠⠆⢸⡇⠀⠀⠀⠀⠀⠀⠀⡇⣹⣣⢾⢱⣋⣾⣄⣸⠈⣧⠙⠂⠹⡄⠀⠀⢸⡄⠘⡿⢱⣣⣾⣿⣿⢹⡙⣎⣷⢰⡇⣇⠀⡼⡞⢀⡏⠀⣿⡇⠀⠀⠀
⠤⣀⣈⣀⡤⠴⠒⠁⡇⠀⠀⠀⠀⠀⠀⠀⡇⣇⣿⣸⣞⣩⣿⣷⣿⢭⣹⠀⠀⠀⠙⢦⠀⠀⢧⡞⠁⣾⣭⣿⣿⡯⣽⠇⢸⣾⡾⠀⢸⢠⠇⠁⡼⠀⠀⡟⡇⠀⠀⠀
⠀⠀⠀⢀⡇⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⢀⡇⠹⠆⠻⢹⡃⠙⠻⢟⠀⡿⠀⠀⠀⠀⢠⢗⣄⡈⣇⠀⢹⣀⠙⠯⡄⡿⠀⠘⢸⡇⠀⢸⡎⢀⣼⡇⠀⠀⠀⠈⠀⠀⠀
⠀⠀⠀⢸⠁⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⢸⠇⠀⠀⠀⠀⠙⠚⠀⠘⠚⠁⠀⠀⠀⢠⠿⠋⠀⠙⠺⠆⠀⠙⠒⠒⠊⠀⠀⠀⣼⠀⠀⢸⠀⠈⣿⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠈⢺⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡇⣰⠆⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣰⢿⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡰⠃⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠉⢸⠀⠀⠀⢠⡇⠀⠀⠀⠀⠀⠀⢸⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠁⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⡼⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⢸⡇⡷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠠⠖⠦⠤⠤⠀⠤⠠⠀⠀⠀⠀⠀⠀⠀⢀⠜⢹⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⡇⠀⠀⠀⢸⢧⠀⢰⠀⠀⠀⠀⠀⣇⡇⢨⠗⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⠞⡇⠀⢸⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⡀⡇⠀⠀⠀⡏⢸⠀⢰⠀⠀⠀⠀⠀⣿⣁⡼⠤⠖⢻⠢⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⠚⡟⠀⠀⡇⠀⢸⠀⠀⠀⠀⠀⢀⢹⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢃⠇⠀⠀⢀⡇⢸⠀⠚⡆⠀⠀⠀⠀⣿⠹⡀⠀⠀⢸⠀⠀⠉⠓⠦⣄⡀⠀⠀⠀⠀⣀⡴⠚⠉⠉⣳⢧⡀⠀⡇⠀⢸⠀⠀⠀⠀⠀⢸⢸⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢼⠀⠀⠀⢸⠀⠈⡆⢸⣇⠀⠀⠀⠀⣷⠀⠈⠓⠢⠼⣄⣀⣀⠀⠀⠈⠙⠻⢶⣶⣿⢿⣡⠤⠖⠊⠁⢸⠃⠀⡇⠀⢸⠀⠀⠀⠀⡇⣸⢸⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣸⠀⠀⠀⡞⠀⠀⡇⠈⣿⡀⠀⠀⠀⣿⡆⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠒⠢⢄⣀⡴⠋⠀⠀⠀⠀⠀⡾⠀⠀⢻⠀⢸⠀⠀⠀⢸⠁⡇⢸⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠈⡇⠀⠀⢰⠃⣀⣀⣳⠀⣧⣇⠀⠀⠀⢹⢽⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⠀⠀⠀⠀⠀⠀⢰⣋⡉⠳⣼⣤⣼⠀⠀⠀⣼⢠⡇⢸⡇⠀⠀⠀⠀⠀⠀⠀
⠀⢠⠃⣠⡶⠟⠛⢉⣉⣹⡄⢻⣘⡆⠀⠀⢸⠀⠈⠲⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⢀⡏⠁⠙⢦⣀⣀⣸⠀⠀⢠⡟⢸⠙⠻⣅⠀⠀⠀⠀⠀⠀⠀
⠀⣸⡾⠋⢀⠔⠋⠁⠀⠀⣇⢸⠀⠸⡄⠀⢸⡀⠀⠘⢮⡙⠢⢄⡀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⣠⢆⡄⠀⠀⠀⠀⠀⡇⠀⢀⡏⡇⡏⠑⢦⡈⢷⡀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """,
        "": r"""
⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠓⠾⠁⠀⠀⣰⠟⠀⠀⢀⡾⠋⠀⠀⠀⢀⣴⣆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣠⣤⣤⣤⣄⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠙⠳⣦⣴⠟⠁⠀⠀⣠⡴⠋⠀⠈⢷⣄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣴⣶⣿⣿⣿⣿⡿⠿⠿⠿⠿⠿⠿⣿⣿⣿⣿⣷⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⠋⠀⠀⢀⣴⠟⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣶⣿⣿⡿⠟⠋⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠙⠻⢿⣿⣿⣶⣄⡀⠀⠀⠀⠺⣏⠀⠀⣀⡴⠟⠁⢀⣀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣿⣿⠿⠋⠁⠀⢀⣴⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢶⣬⡙⠿⣿⣿⣶⣄⠀⠀⠙⢷⡾⠋⢀⣤⠾⠋⠙⢷⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⡿⠋⠁⠀⠀⠀⢠⣾⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣦⣠⣤⠽⣿⣦⠈⠙⢿⣿⣷⣄⠀⠀⠀⠺⣏⠁⠀⠀⣀⣼⠿⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⣿⡿⠋⠀⠀⠀⠀⠀⣰⣿⠟⠀⠀⠀⢠⣤⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⣿⣧⠀⠀⠈⢿⣷⣄⠀⠙⢿⣿⣷⣄⠀⠀⠙⣧⡴⠟⠋⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⠏⠀⠀⠀⠀⠀⠀⢷⣿⡟⠀⣰⡆⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⣿⣿⡀⠀⠀⠈⢿⣿⣦⠀⠀⠙⢿⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⡿⠁⠀⠦⣤⣀⠀⠀⢀⣿⣿⡇⢰⣿⠇⠀⢸⣿⡆⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⢸⣿⣿⣆⠀⠀⠈⣿⣿⣧⣠⣤⠾⢿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⣵⣿⠀⠀⠀⠉⠀⠀⣼⣿⢿⡇⣾⣿⠀⠀⣾⣿⡇⢸⠀⠀⠀⠀⠀⠀⣿⡇⠀⣼⣿⢻⣿⣦⠴⠶⢿⣿⣿⣇⠀⠀⠀⢻⣿⣧⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⢠⣿⡟⡌⣼⣿⣿⠉⢁⣿⣿⣷⣿⡗⠒⠚⠛⠛⢛⣿⣯⣯⣿⣿⠀⢻⣿⣧⠀⢸⣿⣿⣿⡄⠀⠀⠀⠙⢿⣿⣷⣤⣀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⢸⣿⡇⣼⣿⣿⣿⣶⣾⣿⣿⢿⣿⡇⠀⠀⠀⠀⢸⣿⠟⢻⣿⣿⣿⣶⣿⣿⣧⢸⣿⣿⣿⣧⠀⠀⠀⢰⣷⡈⠛⢿⣿⣿⣶⣦⣤⣤⣀
⠀⠀⠀⠀⢀⣤⣾⣿⣿⢫⡄⠀⠀⠀⠀⠀⠀⣿⣿⣹⣿⠏⢹⣿⣿⣿⣿⣿⣼⣿⠃⠀⠀⠀⢀⣿⡿⢀⣿⣿⠟⠀⠀⠀⠹⣿⣿⣿⠇⢿⣿⡄⠀⠀⠈⢿⣿⣷⣶⣶⣿⣿⣿⣿⣿⡿
⣴⣶⣶⣿⣿⣿⣿⣋⣴⣿⣇⠀⠀⠀⠀⠀⢀⣿⣿⣿⣟⣴⠟⢿⣿⠟⣿⣿⣿⣿⣶⣶⣶⣶⣾⣿⣿⣿⠿⣫⣤⣶⡆⠀⠀⣻⣿⣿⣶⣸⣿⣷⡀⠀⠀⠸⣿⣿⣿⡟⠛⠛⠛⠉⠁⠀
⠻⣿⣿⣿⣿⣿⣿⡿⢿⣿⠋⠀⢠⠀⠀⠀⢸⣿⣿⣿⣿⣁⣀⣀⣁⠀⠀⠉⠉⠉⠉⠉⠉⠉⠁⠀⠀⠀⠸⢟⣫⣥⣶⣿⣿⣿⠿⠟⠋⢻⣿⡟⣇⣠⡤⠀⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠉⠉⢹⣿⡇⣾⣿⠀⠀⢸⡆⠀⠀⢸⣿⣿⡟⠿⠿⠿⠿⣿⣿⣿⣿⣷⣦⡄⠀⠀⠀⠀⠀⠀⢠⣾⣿⣿⣿⣿⣯⣥⣤⣄⣀⡀⢸⣿⠇⢿⢸⡇⠀⢹⣿⣿⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣾⣿⡇⣿⣿⠀⠀⠸⣧⠀⠀⢸⣿⣿⠀⢀⣀⣤⣤⣶⣾⣿⠿⠟⠛⠁⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠙⠛⢛⣛⠛⠛⠛⠃⠸⣿⣆⢸⣿⣇⠀⢸⣿⣿⣿⣷⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢻⣿⡇⢻⣿⡄⠀⠀⣿⡄⠀⢸⣿⡷⢾⣿⠿⠟⠛⠉⠉⠀⠀⠀⢠⣶⣾⣿⣿⣿⣿⣿⣶⣶⠀⠀⢀⡾⠋⠁⢠⡄⠀⣤⠀⢹⣿⣦⣿⡇⠀⢸⣿⣿⣿⣿⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢸⣿⣇⢸⣿⡇⠀⠀⣿⣧⠀⠈⣿⣷⠀⠀⢀⣀⠀⢙⣧⠀⠀⠀⢸⣿⡇⠀⠀⠀⠀⢀⣿⡏⠀⠀⠸⣇⠀⠀⠘⠛⠘⠛⠀⢀⣿⣿⣿⡇⠀⣼⣿⢻⣿⡿⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠸⣿⣿⣸⣿⣿⠀⠀⣿⣿⣆⠀⢿⣿⡀⠀⠸⠟⠀⠛⣿⠃⠀⠀⢸⣿⡇⠀⠀⠀⠀⢸⣿⡇⠀⠀⠀⠙⠷⣦⣄⡀⠀⢀⣴⣿⡿⣱⣾⠁⠀⣿⣿⣾⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⣿⣇⠀⢿⢹⣿⣆⢸⣿⣧⣀⠀⠀⠴⠞⠁⠀⠀⠀⠸⣿⡇⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⢀⣨⣽⣾⣿⣿⡏⢀⣿⣿⠀⣸⣿⣿⣿⡿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⣿⣆⢸⡏⠻⣿⣦⣿⣿⣿⣿⣶⣦⣤⣀⣀⣀⣀⠀⣿⣷⠀⠀⠀⣸⣿⣏⣀⣤⣤⣶⣾⣿⣿⣿⠿⠛⢹⣿⣧⣼⣿⣿⣰⣿⣿⠛⠛⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠙⣿⣿⣦⣷⠀⢻⣿⣿⣿⣿⡝⠛⠻⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠟⠛⠛⠉⠁⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣄⢸⣿⣿⣿⣿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⠟⠻⣿⡿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """
    }

    return arte_ascii.get(emocion, arte_ascii.get(""))

def extraer_emociones(texto):
    # Buscar emociones en el texto
    emociones = re.findall(r'\[([^\]]+)\]', texto)
    
    # Eliminar las emociones del texto
    texto_sin_emociones = re.sub(r'\[[^\]]+\]', '', texto)
    
    # Buscar texto entre asteriscos
    texto_entre_asteriscos = re.findall(r'\*([^*]+)\*', texto)

    # Eliminar texto entre asteriscos
    texto_sin_emociones = re.sub(r'\*([^*]+)\*', '', texto_sin_emociones)
    
    return texto_sin_emociones.strip(), emociones, texto_entre_asteriscos


def speak_text_with_edge_tts(text):
    """Convierte el texto en voz utilizando Edge TTS"""
    try:
        # Crear un archivo temporal para almacenar el audio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio_file:
            output_file_path = temp_audio_file.name

        # Agregar comillas alrededor del texto
        quoted_text = f'"{text}"'
        # Ejecutar el comando edge-tts para convertir el texto en audio
        command = [
            "edge-tts",
            "--rate=+15%",
            "--voice",
            "es-PA-MargaritaNeural",
            "--text",
            quoted_text,
            "--write-media",
            output_file_path
        ]

        subprocess.run(command, capture_output=True)

        # Reproducir el archivo de audio resultante
        if os.path.exists(output_file_path):
            try:
                play_audio(output_file_path)
            except Exception as e:
                print(f"*se confunde*")
        else:
            print("*se traba al hablar*")
    except Exception as e:
        print(f"*se hace la oidos sordos*")

# Función para reproducir audio con pygame y esperar a que termine
def play_audio(audio_file):
    # Cargar el archivo de audio
    sound = pygame.mixer.Sound(audio_file)
    # Reproducir el audio
    sound.play()
    # Esperar a que termine el audio
    while pygame.mixer.get_busy():
        time.sleep(0.1)

# Reemplaza la función speak_text con speak_text_with_edge_tts
def speak_text(text):
    speak_text_with_edge_tts(text)

def _old_loop(gpt4all_instance):
    initial_message = read_initial_message()
    while True:

        message = read_message_from_file('messages.txt')

        if message != prev_message:
            prev_message = message
        else:
            time.sleep(1)
            continue
        # Check if special command and take action
        if message in SPECIAL_COMMANDS:
            SPECIAL_COMMANDS[message](MESSAGES)
            continue

        # if regular message, append to messages
        MESSAGES.append({"role": "user", "content": message})

        # execute chat completion and ignore the full response since 
        # we are outputting it incrementally
        full_response = gpt4all_instance.chat_completion(
            MESSAGES,
                # preferential kwargs for chat ux
            logits_size=0,
            tokens_size=0,
            n_past=0,
            n_ctx=0,
            n_predict=200,
            top_k=40,
            top_p=0.9,
            min_p=0.0,
            temp=0.9,
            n_batch=9,
            repeat_penalty=1.1,
            repeat_last_n=64,
            context_erase=0.0,
                # required kwargs for cli ux (incremental response)
            verbose=False,
            streaming=True,
            )
        # record assistant's response to messages
        response_message = full_response.get("choices")[0].get("message")
        MESSAGES.append(response_message)
            
        # Convertir la respuesta del asistente en voz
        speak_text(response_message["content"])
        #print()  # newline before next prompt


def _new_loop(gpt4all_instance):
    global read_initial, initial2
    initial_message = read_initial_prompt()
    #prompt_template = 'response:\n{0}\n\nuser:\n'
    os.system ("cls")
    emocion=mostrar_emocion("Aliviada")
    print(emocion)
    print("*espera a que se conecten sus seguidores*") 
    prev_message = ""                   
    chat_session = gpt4all_instance.chat_session(system_prompt=initial_message)
    
    with chat_session:
        salida_texto=""
        while True:
            if read_initial==False:
                message = read_initial_message()
                max_tokens=10
                read_initial=True
            else:
                message = message = read_message_from_file('messages.txt')
                max_tokens=1000

            if message != prev_message:
                prev_message = message
            else:
                time.sleep(1)
                continue

            # Check if special command and take action
            if message in SPECIAL_COMMANDS:
                SPECIAL_COMMANDS[message](MESSAGES)
                continue

            # if regular message, append to messages
            MESSAGES.append({"role": "user", "content": message})

            # if regular message, append to messages
            MESSAGES.append({"role": "user", "content": message})
            # execute chat completion and ignore the full response since
            # we are outputting it incrementally
            response_generator = gpt4all_instance.generate(
                message,
                max_tokens=max_tokens,
                temp=0.9,
                top_k=40,
                top_p=0.9,
                min_p=0.0,
                repeat_penalty=1.1,
                repeat_last_n=64,
                n_batch=9,
                streaming=True,
                )
            response = io.StringIO()
            chunk = ""
            emociones =["Neutral"]
            texto =""
            emocion=""
            asteriscos=""
            old_emotion=mostrar_emocion("Neutral")

            response_text=""
            for token in response_generator:
                response_text+=token
            response_text+="\n"
            
            for token in response_text:
                response.write(token)
                chunk += token
                if token.endswith("\n") or token.endswith("]"):
                    texto, emociones, asteriscos = extraer_emociones(chunk)
                    if len(emociones)>0:
                        emocion=mostrar_emocion(emociones[0])
                        old_emotion=emocion
                    else:
                        emocion=old_emotion
                    os.system("cls")
                    print(emocion)
                    for i, asterisco in enumerate(asteriscos):
                        # Si no es el último elemento, añadimos un salto de línea
                        if i < len(asteriscos) - 1:
                            print("*" + asterisco + "*")
                        else:
                            print("*" + asterisco + "*")
                    texto=limpiar_texto(texto)
                    if initial2==False:
                        initial2=True
                    else:
                        print(message,end="")
                        
                    if cadena_valida(texto):
                        speak_text(texto)
                    chunk = ""
            # record assistant's response to messages
            response_message = {'role': 'assistant', 'content': response.getvalue()}
            response.close()
            gpt4all_instance.current_chat_session.append(response_message)
            MESSAGES.append(response_message)



@app.command()
def version():
    """The CLI version command."""
    print(f"gpt4all-cli v{VERSION}")
    print(f"gpt4all-cli v{Path.home()}")

if __name__ == "__main__":
    repl()  # Iniciar automáticamente en modo REPL con valores predeterminados
