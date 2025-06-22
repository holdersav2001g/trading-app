import asyncio
import structlog
from .base_worker import BaseWorker

log = structlog.get_logger()

class StrategySimulator(BaseWorker):
    async def handle_message(self, message: dict):
        """
        Simulates handling a medium-priority trading strategy.
        """
        log.info("strategy_simulator.handle_message", message=message)
        # Simulate some async work
        await asyncio.sleep(0.005)