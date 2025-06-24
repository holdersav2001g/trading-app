import asyncio
import signal
import structlog

from .config import settings
from .database.database import SessionLocal, Base, engine
from .logging_config import setup_logging
from .components.data_generator import SimulatedMarketGenerator
from .components.ingestion import DataIngestionBuffer, MessageParser
from .components.monitoring import PerformanceMonitor, AlertSystem
from .components.scheduling import PriorityScheduler
from .components.workers.risk_simulator import RiskSimulator
from .components.workers.strategy_simulator import StrategySimulator
from .components.workers.analytics_engine import AnalyticsEngine

log = structlog.get_logger()

async def main():
    """
    Main function to initialize and run the application components.
    """
    setup_logging()
    log.info("application.startup")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    db_session = SessionLocal()

    # Initialize components
    loop = asyncio.get_running_loop()
    monitor = PerformanceMonitor(db_session, loop)
    alert_system = AlertSystem(db_session)
    
    ingestion_buffer = DataIngestionBuffer(settings.buffer_size)
    market_generator = SimulatedMarketGenerator(settings.message_rate_per_second, ingestion_buffer.buffer)
    
    priority_queue = asyncio.PriorityQueue()
    parser = MessageParser(ingestion_buffer.buffer, priority_queue, monitor, alert_system)

    workers = {
        1: RiskSimulator(),
        2: StrategySimulator(),
        3: AnalyticsEngine()
    }
    scheduler = PriorityScheduler(priority_queue, workers)

    # Start all components as asyncio tasks
    tasks = [
        asyncio.create_task(market_generator.generate_market_data()),
        asyncio.create_task(parser.run()),
        asyncio.create_task(scheduler.run()),
        asyncio.create_task(monitor.run_reporter())
    ]

    log.info("application.running")
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        log.info("application.shutdown_signal_received")
    finally:
        # Stop all tasks
        log.info("application.shutdown")
        market_generator.stop()
        parser.stop()
        scheduler.stop()
        
        # Wait for tasks to finish
        await asyncio.gather(*tasks, return_exceptions=True)
        db_session.close()
        log.info("application.shutdown.complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("application.shutdown_initiated")