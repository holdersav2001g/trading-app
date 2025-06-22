from abc import ABC, abstractmethod
import asyncio

class BaseWorker(ABC):
    @abstractmethod
    async def handle_message(self, message: dict):
        """
        Abstract method to handle incoming messages.
        """
        pass