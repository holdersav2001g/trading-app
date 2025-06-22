import time
import asyncio
from collections import deque
import structlog
from sqlalchemy.orm import Session
from ..database.database import SessionLocal
from ..database.models import PerformanceMetric, Alert

log = structlog.get_logger()

class PerformanceMonitor:
    def __init__(self, db_session: Session, loop: asyncio.AbstractEventLoop):
        self.db_session = db_session
        self.loop = loop
        self.message_count = 0
        self.processing_times = deque(maxlen=1000)
        self.last_report_time = time.monotonic()

    async def record_processing_time(self, start_time: float):
        end_time = time.monotonic()
        self.processing_times.append(end_time - start_time)
        self.message_count += 1

    async def run_reporter(self):
        while True:
            await asyncio.sleep(1)
            now = time.monotonic()
            delta_time = now - self.last_report_time

            if delta_time > 0:
                throughput = self.message_count / delta_time
                avg_latency = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0

                log.info(
                    "performance_report",
                    throughput=throughput,
                    avg_latency_ms=avg_latency * 1000,
                    message_count=self.message_count,
                )

                # Reset for next interval
                self.message_count = 0
                self.last_report_time = now

                # Save to DB
                self.save_metric("throughput", throughput)
                self.save_metric("avg_latency_ms", avg_latency * 1000)

    def save_metric(self, name: str, value: float):
        metric = PerformanceMetric(metric_name=name, value=value)
        self.db_session.add(metric)
        self.db_session.commit()


class AlertSystem:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def send_alert(self, name: str, details: str, severity: str = "info"):
        log.warning("alert_sent", alert_name=name, details=details, severity=severity)
        alert = Alert(alert_name=name, details=details, severity=severity)
        self.db_session.add(alert)
        self.db_session.commit()