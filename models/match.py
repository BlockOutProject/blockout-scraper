from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime

class MatchStatus(Enum):
    UPCOMING = "UPCOMING"
    COMPLETED = "COMPLETED"

@dataclass
class Match:
    match_code: str
    league_code: str
    pool_id: int
    team_id_a: int
    team_id_b: int
    match_date: datetime
    status: MatchStatus
    set: Optional[str] = None
    score: Optional[str] = None
    venue: Optional[str] = None
    referee1: Optional[str] = None
    referee2: Optional[str] = None
    active: bool = True

    def to_dict(self):
        """Convertit l'objet Match en dictionnaire prêt à être envoyé à l'API."""
        return {
            "match_code": self.match_code,
            "league_code": self.league_code,
            "pool_id": self.pool_id,
            "team_id_a": self.team_id_a,
            "team_id_b": self.team_id_b,
            "match_date": self.match_date.isoformat(),
            "status": self.status.value,
            "set": self.set,
            "score": self.score,
            "venue": self.venue,
            "referee1": self.referee1,
            "referee2": self.referee2,
            "active": self.active
        }