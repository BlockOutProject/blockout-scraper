from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Team:
    club_id: str
    pool_id: int
    team_name: str
    team_alias: Optional[str] = None
    last_update: Optional[datetime] = None
    id: Optional[int] = None
    active: bool = True
