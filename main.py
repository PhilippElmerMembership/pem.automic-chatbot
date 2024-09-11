import os
import json
import openai

from typing import Dict, Optional
from dotenv import load_dotenv, find_dotenv

from prompts.system_prompt import pirate as system_prompt

from utils.messagecache import MemoryCache, MessageCache
from utils.decorator import get_openai_funcs

# Decorator registriert tool, d.h. ist import notwendig
from tools.automic import *
from tools.file import *


load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")

# Maximale Anzahl Funktionsaufrufe in einer Verarbeitung von GPT
MAX_FUNC_CALL = 10
# Maximale Anzahl von Chatnachrichten, an die sich der Bot erinnern kann (Systemmessage wird jeweils beibehalten)
CONTEXT_WINDOW = 15
# Kreativität der Antworten
TEMPERATURE = 0.8
# Zu verwendendes AI Model
MODEL = "gpt-4-turbo"
# Informiert über Funktionsaufrufe (steuerbar mit !debug)
DEBUG = False

# Der Nachrichten Cache merkt sich die letzen X Nachrichten im Chatverlauf. Das ist das "Gedächtnis".
# Die Systemnachricht ist dabei das Regelwerk / der Charakter, welcher immer mitgegeben wird.
message_cache = MemoryCache(
    system_message=system_prompt,
    size=CONTEXT_WINDOW,
)


def call_openai(message_cache: MessageCache) -> Dict:
    """Aufruf an OpenAI um den Chat zu "vervollständigen".

    Args:
        messages (List[str]): Nachrichtenhistory

    Returns:
        str: Antwort / Vervollständigung
    """
    return openai.chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        messages=message_cache.get_messages(),
        functions=get_openai_funcs(),
        function_call="auto",
    )


def welcome_header():
    """Begrüssung"""
    print(f"☝: Verwende CRTL-C um den Chat zu verlassen.")
    print()


def process_command(cmd: str):
    if cmd == "!exit":
        raise KeyboardInterrupt()

    if cmd == "!debug":
        global DEBUG
        DEBUG = not DEBUG
        print(f"⚡: DEBUG Modus ist jetzt {DEBUG}")
        return

    if cmd == "!history":
        for message in message_cache.get_messages():
            print(message)
        return

    print(f"💥: Unbekannter Befehl {cmd}")


def goodbye_footer():
    """Verabschiedung"""
    print()
    print()
    print(f"👋: Danke fürs vorbeischauen!")


def call_function(
    function_name: str, function_args: Optional[str] = None
) -> Optional[Dict]:
    """Funktionsaufruf durch den ChatBot

    Args:
        function_name (str): Name der zu startenden Funktion
        function_args (Optional[str], optional): Parameter, falls zutreffend. Defaults to None.

    Raises:
        NotImplementedError: (Versuchter) Aufruf einer nicht implementierten Funktion.

    Returns:
        str: Identifizierte Folgefunktion (falls zutreffend)
    """
    message = f"Funktionaufruf {function_name} mit Argumenten {function_args}"
    if DEBUG:
        print(f"⚡: {message}")

    # Bezieht aus der Liste von Funktionen diejenige, welche mit dem beantragten Namen übereinstimmt.
    runner = globals().get(function_name)
    if not runner:
        raise NotImplementedError(
            f"💥: Unbekannte Funktion wurde beantragt: {function_name}"
        )

    # Funktion mit gegebenen Parametern ausführen.
    args = None
    if function_args:
        args = json.loads(function_args)

    response = None
    try:
        function_response = runner(**args)

        message_cache.add_message(
            role="function", message=f"{function_response}", name=function_name
        )
        response = call_openai(message_cache=message_cache)
    except Exception as e:
        message_cache.add_message(
            role="function",
            message=f"Funktionsaufruf fehlgeschlagen. Prüfe die Parameter und probiere es erneut.",
            name=function_name,
        )
        print(f"💥: Funktionsaufruf fehlgeschlagen: {e}")

    return response


def conversation_loop():
    """Unterhaltung mit GPT führen"""

    # Eingabe des Benutzers erfassen
    user_msg = input("😬: ")

    if not user_msg:
        return

    # Wenn die Eingabe mit "!" beginnt, wird es als Befehl erkannt
    if user_msg.startswith("!"):
        process_command(cmd=user_msg)
        return

    # Chat führen und prüfen, ob ein Funktionsaufruf beantragt wurde
    message_cache.add_message(role="user", message=user_msg)
    response = call_openai(message_cache=message_cache)

    message = response.choices[0].message
    function = message.function_call

    # Bei einem Funktionsaufruf, diesen Verarbeiten
    func_loop = 0
    while function:
        if func_loop == MAX_FUNC_CALL:
            print(
                f"💥: Funktionsloop wird unterbrochen wegen Erreichen von MAX_FUNC_CALL!"
            )
            message_cache.add_message(
                role="user",
                message=f"Mehr kann ich dir nicht ausfindig machen, da ich nur {MAX_FUNC_CALL} Tools nacheinander aufrufen kann. Bitte sag das dem Benutzer.",
            )
            # Sicherstellen, dass der Fehler als Chatnachricht formatiert wird.
            response = call_openai(message_cache=message_cache)
            break

        func_loop += 1

        response = call_function(
            function_name=function.name,
            function_args=function.arguments,
        )

        if not response:
            break

        function = response.choices[0].message.function_call

    # Antwort von GPT zurückgeben
    if response:
        robot_msg = response.choices[0].message.content
    else:
        robot_msg = "Ich habe keine Antwort für dich. 😕"

    message_cache.add_message(role="assistant", message=robot_msg)
    print(f"🤖: {robot_msg}")


def main():
    """Loop Kontrolle"""
    welcome_header()

    while True:
        try:
            conversation_loop()
        except KeyboardInterrupt:
            goodbye_footer()
            exit(0)


if __name__ == "__main__":
    main()
