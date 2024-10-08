# session_manager.py
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from db import engine
import logging

# Importer le logger
logger = logging.getLogger('myvolley')

# Fabrique de sessions pour la base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session():
    """
    Fournit un contexte transactionnel autour d'une série d'opérations.
    Gère automatiquement le commit ou le rollback en cas d'erreur.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
        logger.debug("Transaction commitée avec succès.")
    except Exception as e:
        session.rollback()
        logger.error(f"Transaction annulée en raison d'une erreur: {e}", exc_info=True)
        raise
    finally:
        session.close()
        logger.debug("Session fermée.")