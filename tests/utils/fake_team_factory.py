from random import choice, randint
from faker import Faker
from typing import Optional
from datetime import datetime
from models.team import Team


class FakeTeamFactory:
    def __init__(self, seed: Optional[int] = None):
        """
        Initialise une instance de FakeTeamFactory avec Faker.
        Un seed peut être fourni pour des résultats reproductibles.
        """
        self.fake = Faker()
        if seed is not None:
            self.fake.seed_instance(seed)

    def create_active_team(self) -> Team:
        """
        Génère une instance fictive d'une équipe active.
        """
        return Team(
            club_id=self.fake.unique.word().upper(),
            pool_id=self.fake.random_int(min=1, max=100),
            team_name=self.fake.company(),
            team_alias=self.fake.word().capitalize() if choice([True, False]) else None,
            last_update=self.fake.date_time_this_month(),
            id=self.fake.random_int(min=1, max=1000),
            active=True,
        )

    def create_inactive_team(self) -> Team:
        """
        Génère une instance fictive d'une équipe inactive.
        """
        return Team(
            club_id=self.fake.unique.word().upper(),
            pool_id=self.fake.random_int(min=1, max=100),
            team_name=self.fake.company(),
            team_alias=self.fake.word().capitalize() if choice([True, False]) else None,
            last_update=self.fake.date_time_this_month(),
            id=self.fake.random_int(min=1, max=1000),
            active=False,
        )

    def create(self, active: Optional[bool] = None) -> Team:
        """
        Génère une équipe fictive. Si le paramètre `active` est spécifié,
        renvoie une équipe active ou inactive en fonction de la valeur.
        """
        if active is None:
            active = choice([True, False])

        if active:
            return self.create_active_team()
        else:
            return self.create_inactive_team()