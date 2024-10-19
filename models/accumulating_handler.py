import logging

class AccumulatingHandler(logging.Handler):
    """
    Handler qui accumule les logs dans une liste.
    """
    def __init__(self, level=logging.INFO):
        super().__init__(level=level)
        self.log_records = []

    def emit(self, record):
        # Formater le message de log
        log_entry = self.format(record)
        # Ajouter le log formatté à la liste des logs
        self.log_records.append(log_entry)

    def get_logs(self):
        """
        Retourner tous les logs accumulés.
        """
        return self.log_records
    
    def clear_logs(self):
        """
        Réinitialiser la liste des logs accumulés.
        """
        self.log_records = []