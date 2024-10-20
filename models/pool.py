from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class PoolDivisionCode(Enum):
    REG = "REG"
    NAT = "NAT"
    PRO = "PRO"

@dataclass
class Pool:
    pool_code: str
    league_code: str
    season: int
    division_code: PoolDivisionCode
    league_name: Optional[str] = None
    pool_name: Optional[str] = None
    division_name: Optional[str] = None
    gender: Optional[str] = None
    raw_division_name: Optional[str] = None
    active: bool = True

    def to_dict(self):
        """Convertit l'objet Pool en dictionnaire prêt à être envoyé à l'API."""
        return {
            "pool_code": self.pool_code,
            "league_code": self.league_code,
            "season": self.season,
            "division_code": self.division_code.value,
            "league_name": self.league_name,
            "pool_name": self.pool_name,
            "division_name": self.division_name,
            "gender": self.gender,
            "raw_division_name": self.raw_division_name,
            "active": self.active
        }