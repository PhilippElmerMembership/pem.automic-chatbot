from utils.decorator import openaifunc


@openaifunc
def get_object_names_from_file(name: str) -> list[str]:
    """Get object names from file

    LLM instruction:
    This returns a list of object names from a file.

    Args:
        name (str): Name of the file

    Returns:
        list[str]: List of object names
    """

    with open(name, "r") as file:
        return file.readlines()
