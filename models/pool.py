from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class PoolDivisionCode(Enum):
    REG = "REG"
    NAT = "NAT"
    PRO = "PRO"

class PoolGender(Enum):
    M = "M"
    F = "F"

@dataclass
class Pool:
    pool_code: str
    league_code: str
    season: int
    division_code: PoolDivisionCode
    last_update: Optional[datetime] = None
    id: Optional[int] = None
    league_name: Optional[str] = None
    pool_name: Optional[str] = None
    division_name: Optional[str] = None
    gender: Optional[PoolGender] = None
    raw_division_name: Optional[str] = None
    active: bool = True
    
    def to_dict(self) -> dict:
        """
        Convertit l'instance actuelle en un dictionnaire compatible JSON.
        Gère les champs Enum et datetime.
        """
        result = {}
        for key, value in asdict(self).items():
            if isinstance(value, Enum):
                result[key] = value.value  # Convertir Enum en sa valeur
            elif isinstance(value, datetime):
                result[key] = value.isoformat()  # Convertir datetime en format ISO 8601
            else:
                result[key] = value  # Conserver les autres types
        return result
    