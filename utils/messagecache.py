from abc import ABC
from typing import Dict, List, Optional


class MessageCache(ABC):
    """
    The message cache stores the messages that have been sent to OpenAI.
    You could implement a variation that uses a database or a file to store
    the messages, or just keep it in memory as I do with MemoryCache.
    """

    size: int
    system_message: str
    cache: List[str]

    def add_message(self, role: str, message: str, name: Optional[str] = None):
        raise NotImplementedError("Method not implemented.")

    def get_messages(self) -> List[Dict]:
        raise NotImplementedError("Method not implemented.")


class MemoryCache(MessageCache):
    def __init__(self, system_message: str, size: int = 10):
        self.cache = []
        self.size = size
        self.system_message = {"role": "system", "content": system_message}

    def add_message(self, role: str, message: str, name: Optional[str] = None):
        message = {"role": role, "content": message}

        if name:
            message.update({"name": name})

        self.cache.append(message)

    def get_messages(self) -> List[Dict]:
        return [self.system_message] + self.cache[-self.size :]
