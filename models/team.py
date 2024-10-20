from dataclasses import dataclass
from typing import Optional

@dataclass
class Team:
    club_id: str
    pool_id: int
    team_name: str
    active: bool = True

    def to_dict(self):
        """Convertit l'objet Team en dictionnaire prêt à être envoyé à l'API."""
        return {
            "club_id": self.club_id,
            "pool_id": self.pool_id,
            "team_name": self.team_name,
            "active": self.active
        }