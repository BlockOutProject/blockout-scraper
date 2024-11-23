from random import choice, randint
from faker import Faker
from typing import Optional
from datetime import datetime
from models.pool import Pool, PoolDivisionCode


class FakePoolFactory:
    def __init__(self, seed: Optional[int] = None):
        """
        Initialise une instance de FakePoolFactory avec Faker.
        Un seed peut être fourni pour des résultats reproductibles.
        """
        self.fake = Faker()
        if seed is not None:
            self.fake.seed_instance(seed)

    def create_active_pool(self) -> Pool:
        """
        Génère une instance fictive d'une pool active.
        """
        return Pool(
            pool_code=self.fake.unique.word().upper(),
            league_code=self.fake.word(),
            season=self.fake.year(),
            division_code=choice(list(PoolDivisionCode)),
            last_update=self.fake.date_time_this_month(),
            id=self.fake.random_int(min=1, max=1000),
            league_name=self.fake.company(),
            pool_name=self.fake.city(),
            division_name=self.fake.word().capitalize(),
            gender=choice(["M", "F"]),
            raw_division_name=self.fake.word(),
            active=True,
        )

    def create_inactive_pool(self) -> Pool:
        """
        Génère une instance fictive d'une pool inactive.
        """
        return Pool(
            pool_code=self.fake.unique.word().upper(),
            league_code=self.fake.word(),
            season=self.fake.year(),
            division_code=choice(list(PoolDivisionCode)),
            last_update=self.fake.date_time_this_month(),
            id=self.fake.random_int(min=1, max=1000),
            league_name=self.fake.company(),
            pool_name=self.fake.city(),
            division_name=self.fake.word().capitalize(),
            gender=choice(["M", "F"]),
            raw_division_name=self.fake.word(),
            active=False,
        )

    def create(self, active: Optional[bool] = None) -> Pool:
        """
        Génère une pool fictive. Si le paramètre `active` est spécifié,
        renvoie une pool active ou inactive en fonction de la valeur.
        """
        if active is None:
            active = choice([True, False])

        if active:
            return self.create_active_pool()
        else:
            return self.create_inactive_pool()