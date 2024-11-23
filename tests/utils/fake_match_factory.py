from random import choice, randint, shuffle
from faker import Faker
from typing import Optional
from models.match import Match, MatchStatus

class FakeMatchFactory:
    def __init__(self, seed: Optional[int] = None):
        """
        Initialise une instance de FakeMatchFactory avec Faker.
        Un seed peut être fourni pour des résultats reproductibles.
        """
        self.fake = Faker()
        if seed is not None:
            self.fake.seed_instance(seed)

    def _generate_set_and_score(self) -> tuple[str, str]:

        # Liste des scores de sets possibles
        possible_set_scores = ['3-0', '3-1', '3-2', '0-3', '1-3', '2-3']

        # Sélection aléatoire d'un score de set
        set_score = choice(possible_set_scores)

        # Extraction du nombre de sets gagnés par chaque équipe
        sets_won_a, sets_won_b = map(int, set_score.split('-'))

        # Détermination du vainqueur du match
        winner = 'A' if sets_won_a > sets_won_b else 'B'

        # Nombre total de sets joués
        total_sets = sets_won_a + sets_won_b

        # Création de la liste des vainqueurs de chaque set
        # En s'assurant que le dernier set est gagné par le vainqueur du match
        sets_won_a_excl_last = sets_won_a - 1 if winner == 'A' else sets_won_a
        sets_won_b_excl_last = sets_won_b - 1 if winner == 'B' else sets_won_b

        set_wins_excl_last = ['A'] * sets_won_a_excl_last + ['B'] * sets_won_b_excl_last
        shuffle(set_wins_excl_last)

        # Ajout du vainqueur du dernier set
        set_wins = set_wins_excl_last + [winner]

        score_results = []
        for i in range(total_sets):
            # Détermination du nombre de points minimum pour gagner le set
            if total_sets == 5 and i == 4:
                min_winning_points = 15  # Cinquième set décisif
            else:
                min_winning_points = 25  # Sets 1 à 4

            # Détermination si le set a été prolongé au-delà du score minimum
            deuce = randint(0, 1)
            if deuce:
                # Set prolongé au-delà du score minimum
                extra_points = randint(1, 5)  # Nombre de points supplémentaires
                winner_points = min_winning_points + extra_points
                loser_points = winner_points - 2  # Écart de deux points
            else:
                # Set terminé au score minimum
                winner_points = min_winning_points
                # Le perdant peut avoir entre 0 et winner_points - 2 points
                loser_points = randint(winner_points - 10, winner_points - 2)
                # S'assurer que le score du perdant est au moins 0
                loser_points = max(0, loser_points)

            # Formatage du score du set en fonction du vainqueur
            if set_wins[i] == 'A':
                score_results.append(f"{winner_points}-{loser_points}")
            else:
                score_results.append(f"{loser_points}-{winner_points}")

        # Assemblage des scores des sets
        score_summary = ','.join(score_results)

        return set_score, score_summary

    def create_upcoming_match(self) -> Match:
        """
        Génère un match factice avec le statut UPCOMING.
        """
        return Match(
            match_code=self.fake.uuid4(),
            league_code=self.fake.word(),
            pool_id=self.fake.random_int(min=1, max=100),
            team_id_a=self.fake.random_int(min=1, max=50),
            team_id_b=self.fake.random_int(min=51, max=100),
            match_date=self.fake.future_datetime(end_date='+30d'),
            status=MatchStatus.UPCOMING,
            last_update=self.fake.date_time_this_month(),
            id=self.fake.random_int(min=1, max=1000),
            set=None,
            score=None,
            venue=self.fake.city(),
            referee1=self.fake.name(),
            referee2=self.fake.name(),
            live_code=self.fake.random_int(min=1000, max=9999),
            active=choice([True, False])
        )

    def create_finished_match(self) -> Match:
        """
        Génère un match factice avec le statut FINISHED.
        """
        set_summary, score_summary = self._generate_set_and_score()
        return Match(
            match_code=self.fake.uuid4(),
            league_code=self.fake.word(),
            pool_id=self.fake.random_int(min=1, max=100),
            team_id_a=self.fake.random_int(min=1, max=50),
            team_id_b=self.fake.random_int(min=51, max=100),
            match_date=self.fake.past_datetime(start_date='-30d'),
            status=MatchStatus.FINISHED,
            last_update=self.fake.date_time_this_month(),
            id=self.fake.random_int(min=1, max=1000),
            set=set_summary,
            score=score_summary,
            venue=self.fake.city(),
            referee1=self.fake.name(),
            referee2=self.fake.name(),
            live_code=self.fake.random_int(min=1000, max=9999),
            active=choice([True, False])
        )

    def create_active_match(self) -> Match:
        """
        Génère un match factice actif (status UPCOMING ou FINISHED).
        """
        match = self.create(choice([MatchStatus.UPCOMING, MatchStatus.FINISHED]))
        match.active = True
        return match

    def create_inactive_match(self) -> Match:
        """
        Génère un match factice inactif (status UPCOMING ou FINISHED).
        """
        match = self.create(choice([MatchStatus.UPCOMING, MatchStatus.FINISHED]))
        match.active = False
        return match

    def create(self, status: Optional[MatchStatus] = None) -> Match:
        """
        Génère un match factice. Si aucun statut n'est spécifié, choisit
        aléatoirement entre `UPCOMING` et `FINISHED`.
        """
        if status is None:
            status = choice([MatchStatus.UPCOMING, MatchStatus.FINISHED])

        if status == MatchStatus.UPCOMING:
            return self.create_upcoming_match()
        elif status == MatchStatus.FINISHED:
            return self.create_finished_match()
        else:
            raise ValueError(f"Statut non supporté : {status}")