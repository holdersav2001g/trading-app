import asyncio
import structlog
from .base_worker import BaseWorker

log = structlog.get_logger()

class RiskSimulator(BaseWorker):
    async def handle_message(self, message: dict):
        """
        Simulates handling a high-priority risk check.
        """
        log.info("risk_simulator.handle_message", message=message)
        # Simulate some async work
        await asyncio.sleep(0.001)