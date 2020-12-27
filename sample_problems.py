import shelve
import random
from collections import defaultdict
from pprint import pprint
import sys
from math import ceil
from datetime import date


def diff_histogram(problems):
    for field in 'min_difficulty', 'max_difficulty', 'accepted_users':
        hist = defaultdict(int)
        for prob in problems.values():
            hist[getattr(prob, field)] += 1
        print(field)
        max_val = max(hist.values())
        for line in range(10, 0, -1):
            for key in sorted(hist.keys()):
                if hist[key] / max_val > (line - 1) / 10:
                    sys.stdout.write('*')
                else:
                    sys.stdout.write(' ')
            sys.stdout.write('\n')
            sys.stdout.flush()


def get_random_problem(
    problems, min_difficulty, max_difficulty, min_user_ratio=0.2, min_users=50
):
    popularity_factor = 5
    suitable_problems = [
        problem for problem in problems.values()
        if (
            problem.min_difficulty >= min_difficulty
            and problem.max_difficulty <= max_difficulty
            and problem.accepted_users >= min_users
            and problem.users_ratio and problem.users_ratio >= min_user_ratio
        )
    ]
    max_users = max(p.accepted_users for p in suitable_problems)
    return random.choices(
        suitable_problems,
        [
            ceil(popularity_factor * p.accepted_users / max_users)
            for p in suitable_problems
        ]
    )[0]


def print_problem(problem):
    diff = (
        f'{problem.min_difficulty/10:.1f}'
        if problem.min_difficulty == problem.max_difficulty
        else f'{problem.min_difficulty/10:.1f} - {problem.max_difficulty/10:.1f}'
    )
    print(f'''{problem.problem_name}
https://open.kattis.com/problems/{problem.problem_id}
Difficulty: {diff}, solved by {problem.accepted_users}/{problem.total_users}''')


def main():
    verbose = '-v' in sys.argv
    with shelve.open('problem_db', 'r') as db:
        problems = db['problems']
        with shelve.open('selected_db', 'c') as selected:
            today = str(date.today())
            if '-f' not in sys.argv and today in selected:
                print('Using previously sampled problems, -f to override', file=sys.stderr)
                if verbose:
                    for problem in selected[today]:
                        print_problem(problem)
                        print()
                return
            s_problem = get_random_problem(problems, 00, 25)
            m_problem = get_random_problem(problems, 25, 60)
            l_problem = get_random_problem(problems, 60, 99)
            selected[today] = (s_problem, m_problem, l_problem)
            if verbose:
                for problem in selected[today]:
                    print_problem(problem)
                    print()


if __name__ == '__main__':
    main()
