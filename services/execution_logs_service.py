from datetime import datetime
from sqlalchemy.orm import Session
from models.execution_log import ExecutionLog

def log_execution(session: Session, start_time: datetime, duration: int, status: str, logs: list):
    """
    Enregistre un log d'exécution dans la base de données.

    Parameters:
    - session (Session): La session SQLAlchemy active.
    - start_time (datetime): Le timestamp du début de l'exécution.
    - duration (int): La durée de l'exécution en secondes.
    - status (str): Le statut de l'exécution ('Success' ou 'Failed').
    """
    log_text = "\n".join(logs)
    
    execution_log = ExecutionLog(
        start_time=start_time,
        duration=duration,
        status=status,
        changes=log_text
    )
    session.add(execution_log)
