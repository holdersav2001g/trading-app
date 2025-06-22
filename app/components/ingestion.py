import asyncio
import json
import time
from collections import deque
import structlog
from .monitoring import PerformanceMonitor, AlertSystem

log = structlog.get_logger()

class DataIngestionBuffer:
    def __init__(self, buffer_size: int):
        self.buffer = asyncio.Queue(maxsize=buffer_size)

    async def put(self, item):
        await self.buffer.put(item)

    async def get(self):
        return await self.buffer.get()

class MessageParser:
    def __init__(self, input_buffer: asyncio.Queue, output_queue: asyncio.Queue, monitor: PerformanceMonitor, alert_system: AlertSystem):
        self.input_buffer = input_buffer
        self.output_queue = output_queue
        self.monitor = monitor
        self.alert_system = alert_system
        self._running = False

    async def run(self):
        self._running = True
        log.info("message_parser.started")
        while self._running:
            raw_message = await self.input_buffer.get()
            start_time = time.monotonic()
            try:
                message = json.loads(raw_message)
                # Basic validation
                if "type" not in message or "symbol" not in message:
                    raise ValueError("Missing required fields")
                
                # Assign priority
                priority = 1 if message["type"] == "trade" else 2
                await self.output_queue.put((priority, message))
                await self.monitor.record_processing_time(start_time)

            except (json.JSONDecodeError, ValueError) as e:
                self.alert_system.send_alert("parsing_error", f"Failed to parse message: {raw_message}, error: {e}", "error")
                await self.monitor.record_processing_time(start_time) # Still record time for failed attempt

    def stop(self):
        self._running = False
        log.info("message_parser.stopped")