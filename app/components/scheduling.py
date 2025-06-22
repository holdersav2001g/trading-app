import asyncio
import structlog
from typing import Dict, Coroutine

log = structlog.get_logger()

class PriorityScheduler:
    def __init__(self, input_queue: asyncio.PriorityQueue, workers: Dict[int, Coroutine]):
        self.input_queue = input_queue
        self.workers = workers
        self._running = False

    async def run(self):
        """
        Continuously fetches tasks from the priority queue and assigns them to the appropriate worker.
        """
        self._running = True
        log.info("priority_scheduler.started")
        while self._running:
            priority, message = await self.input_queue.get()
            worker = self.workers.get(priority)
            if worker:
                asyncio.create_task(worker.handle_message(message))
            else:
                log.warning("priority_scheduler.unknown_priority", priority=priority, message=message)
            self.input_queue.task_done()

    def stop(self):
        """
        Stops the scheduler.
        """
        self._running = False
        log.info("priority_scheduler.stopped")