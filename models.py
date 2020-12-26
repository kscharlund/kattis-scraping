from dataclasses import dataclass


@dataclass(frozen=True)
class Problem:
    problem_id: str
    problem_name: str
    total_submissions: int
    accepted_submissions: int
    submissions_ratio: float
    fastest_submission: float
    total_users: int
    accepted_users: int
    users_ratio: float
    min_difficulty: int
    max_difficulty: int

    def __str__(self):
        return ' '.join((self.problem_id, self.problem_name))
