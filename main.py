import os
import json
import openai

from typing import Dict, Optional
from dotenv import load_dotenv

from prompts.system_prompt import default as system_prompt

from utils.messagecache import MemoryCache, MessageCache
from utils.decorator import get_openai_funcs

from tools.automic import *

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Maximum of function calls that can be made during the handling of one user request.
MAX_FUNC_CALL = os.getenv("MAX_FUNC_CALL", 10)
# Maximum number of messages to send to OpenAI (history)
CONTEXT_WINDOW = os.getenv("CONTEXT_WINDOW", 15)
# Creativity of the AI response.
TEMPERATURE = os.getenv("TEMPERATURE", 0.8)
# Model to use for the chatbot
MODEL = os.getenv("LLM")
# Gives details on function call requests (can be activated using !debug)
DEBUG = False

# The cache stores the messages that have been sent to OpenAI so far. This is necessary to keep the context of the conversation.
message_cache = MemoryCache(
    system_message=system_prompt,
    size=CONTEXT_WINDOW,
)


def call_openai(message_cache: MessageCache) -> Dict:
    """
    Call the chatcompletion api.

    Args:
        messages (List[str]): History of messages

    Returns:
        str: Answer from the AI
    """

    return openai.chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        messages=message_cache.get_messages(),
        functions=get_openai_funcs(),
        function_call="auto",
    )


def welcome_header():
    """
    This is how every chat starts.
    """

    print(f"☝: Use CRTL-C or enter !exit to end the chat")
    print(f"☝: Enter !debug to toggle debug messages.")
    print(f"☝: Enter !history to see the message cache.")
    print()


def process_command(cmd: str):
    """
    Process chatbot command that was entered by the user. These are identified by a leading !.

    Args:
        cmd (str): Command entered by the user
    """

    if cmd == "!exit":
        raise KeyboardInterrupt()

    if cmd == "!debug":
        global DEBUG
        DEBUG = not DEBUG
        print(f"⚡: DEBUG mode is {DEBUG}")
        return

    if cmd == "!history":
        for message in message_cache.get_messages():
            print(message)
        return

    print(f"💥: Unknown command {cmd}")


def goodbye_footer():
    """
    This is how every chat ends.
    """

    print()
    print()
    print(f"👋: Goodbye!")


def call_function(
    function_name: str, function_args: Optional[str] = None
) -> Optional[Dict]:
    """
    Process an LLM request to call a tool.

    Args:
        function_name (str): Name of requested function to call.
        function_args (Optional[str], optional): Parameters. Defaults to None.

    Raises:
        NotImplementedError: LLM tried to call an invalid function. This should never happen.

    Returns:
        str: Identified follow-up function.
    """

    message = f"Function call {function_name} with arguments {function_args}"
    if DEBUG:
        print(f"⚡: {message}")

    # Try to get registered function.
    runner = globals().get(function_name)
    if not runner:
        raise NotImplementedError(
            f"💥: Unknown function was requested: {function_name}"
        )

    # Call function with parameters requested by LLM.
    args = None
    if function_args:
        args = json.loads(function_args)

    response = None
    try:
        function_call_result = runner(**args)
    except Exception as e:
        function_call_result = e
        print(f"💥: Function call failed: {e}")

    message_cache.add_message(
        role="function",
        message=f"Function call {function_name} with arguments {function_args} result:\n{function_call_result}",
        name=function_name,
    )
    response = call_openai(message_cache=message_cache)

    return response


def function_loop(function: Dict, message_cache: MessageCache):
    """
    Process a function call requests from the AI. This loops until either all function call requests are processed or a loop prevention stops further tool calling.

    Args:
        function (Dict): Function call request from the AI.
        message_cache (MessageCache): Cache of messages sent to OpenAI.
    """

    func_loop = 0
    while function:
        if func_loop == MAX_FUNC_CALL:
            print(f"💥: Cancelling loop because of too many function calls.")

            message_cache.add_message(
                role="user",
                message=f"I already called {MAX_FUNC_CALL} functions. Please tell the user that a loop prevention stopped further tool calling.",
            )
            # Let the feedback be processed by the AI.
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

    return response


def conversation_loop():
    """
    This is the chat loop.
    """

    user_msg = input("😬: ")

    if not user_msg:
        return

    # If the input starts with !, it is interpreted as command for the chatbot software. So we won't send this to the LLM.
    if user_msg.startswith("!"):
        process_command(cmd=user_msg)
        return

    # Add user input to chat history and call the autocompletion API.
    message_cache.add_message(role="user", message=user_msg)
    response = call_openai(message_cache=message_cache)

    # Extract the LLM answer and the function to call (if any).
    message = response.choices[0].message
    function = message.function_call

    # If a function call was requested, we enter the function loop.
    if function:
        response = function_loop(function=function, message_cache=message_cache)

    # Show response to the user.
    if response:
        robot_msg = response.choices[0].message.content
    else:
        robot_msg = "LLM did not answer anything 😕"

    message_cache.add_message(role="assistant", message=robot_msg)
    print(f"🤖: {robot_msg}")


def main():
    """
    Main loop
    """
    welcome_header()

    while True:
        try:
            conversation_loop()
        except KeyboardInterrupt:
            goodbye_footer()
            exit(0)


if __name__ == "__main__":
    main()
