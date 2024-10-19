from sqlalchemy import Column, Integer, DateTime, String
from .base import Base

class ExecutionLog(Base):
    __tablename__ = 'execution_logs'

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False) 
    duration = Column(Integer, nullable=False) 
    status = Column(String, nullable=False)  
    changes = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<ExecutionLog(start_time={self.start_time}, duration={self.duration}, status={self.status})>"