import os
import requests

from dotenv import load_dotenv

from utils.decorator import openaifunc

load_dotenv()

AUTOMIC_ENDPOINT = os.getenv("AUTOMIC_ENDPOINT")
AUTOMIC_AUTH = (os.getenv("AUTOMIC_USERNAME"), os.getenv("AUTOMIC_PASSWORD"))


@openaifunc
def find_object(name: str) -> str:
    """Find an automic object

    LLM instruction:
    Only return object names.

    Args:
        name (str): Name of the object

    Returns:
        str: JSON list of objects matching the object name.
    """
    search_object = requests.post(
        url=AUTOMIC_ENDPOINT + "/search",
        auth=AUTOMIC_AUTH,
        json={
            "filters": [{"filter_identifier": "object_name", "object_name": name}],
        },
    )

    return search_object.content


@openaifunc
def start_object(name: str) -> str:
    """Start an automic object

    LLM instruction:
    Always feedback the runid when an object was started.

    Args:
        name (str): Name of the object

    Returns:
        str: JSON encoded RunID identifying the execution.
    """
    search_object = requests.post(
        url=AUTOMIC_ENDPOINT + "/executions",
        auth=AUTOMIC_AUTH,
        json={"object_name": name},
    )

    return search_object.content
