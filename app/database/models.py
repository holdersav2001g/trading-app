import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from .database import Base

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    metric_name = Column(String, index=True)
    value = Column(Float)
    tags = Column(String, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    alert_name = Column(String, index=True)
    details = Column(String)
    severity = Column(String)