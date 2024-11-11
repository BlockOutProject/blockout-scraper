from typing import Optional


class StandardizationError(Exception):
    """Exception levée pour les erreurs de standardisation des divisions."""
    pass

class SeasonParsingError(Exception):
    """Exception levée pour les erreurs de parsing de saison."""
    pass

class URLExtractionError(Exception):
    """Exception levée pour les erreurs d'extraction de saison depuis une URL."""
    pass

class DivisionExtractionError(Exception):
    """Exception levée pour les erreurs d'extraction de division."""
    pass

class TeamAliasError(Exception):
    """Exception levée pour les erreurs liées aux alias d'équipe."""
    pass

class AliasNotFoundError(TeamAliasError):
    """Exception levée lorsque le nom ou l'alias n'est pas trouvé."""
    pass

class GenderMismatchError(TeamAliasError):
    """Exception levée lorsque le genre ne correspond pas."""
    pass

class CSVDownloadError(Exception):
    """Erreur levée lors du téléchargement du fichier CSV."""
    pass

class CSVParsingError(Exception):
    """Erreur levée lors du parsing du fichier CSV."""
    pass

class MatchProcessingError(Exception):
    """Erreur levée lors du traitement des matchs."""
    pass

class FetchError(Exception):
    """Erreur levée lors de la récupération de contenu depuis une URL."""
    pass