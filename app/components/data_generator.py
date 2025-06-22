import asyncio
import random
import time
import json
import structlog

log = structlog.get_logger()

class SimulatedMarketGenerator:
    def __init__(self, message_rate_per_second: int, buffer: asyncio.Queue):
        self.message_rate_per_second = message_rate_per_second
        self.buffer = buffer
        self._running = False

    async def generate_market_data(self):
        """
        Generates simulated market data and puts it into the buffer.
        """
        self._running = True
        log.info("market_data_generator.started")
        while self._running:
            message = {
                "type": random.choice(["quote", "trade"]),
                "symbol": f"SYM{random.randint(1, 10)}",
                "price": round(random.uniform(100, 200), 2),
                "size": random.randint(1, 100),
                "timestamp": time.time()
            }
            await self.buffer.put(json.dumps(message))
            await asyncio.sleep(1.0 / self.message_rate_per_second)

    def stop(self):
        """
        Stops the data generator.
        """
        self._running = False
        log.info("market_data_generator.stopped")