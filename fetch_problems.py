#!/Users/kalle/venv/kattisscraping/bin/python

import sys
import shelve
import time
import requests
from bs4 import BeautifulSoup

from models import Problem

KATTIS_SERVER = 'https://open.kattis.com'
PROBLEM_LIST_PATH = '/problems'
REQUEST_HEADERS = {
    'User-Agent': 'KattisArchiveBot/0.0 (kalle@scharlund.se)',
}


def fetch_problem_pages(verbose):
    page_path = PROBLEM_LIST_PATH
    while page_path:
        if verbose:
            print('Fetching', KATTIS_SERVER + page_path)
        req = requests.get(KATTIS_SERVER + page_path, headers=REQUEST_HEADERS)
        soup = BeautifulSoup(req.text, 'html.parser')
        next_link = soup.find(id='problem_list_next')
        if 'disabled' in next_link['class']:
            page_path = ''
        else:
            page_path = next_link['href']
        yield soup


def parse_title_cell(cell):
    if 'name_column' not in cell['class']:
        raise ValueError(
            'Expected a name column first. Has the format changed?'
        )
    link = cell.a['href']
    link_elements = link.split('/')
    if len(link_elements) != 3 or link_elements[0] or link_elements[1] != 'problems':
        raise ValueError('Unexpected problem link format ' + link)
    problem_id = str(link_elements[-1])
    problem_name = str(cell.string)
    return problem_id, problem_name


def parse_difficulty_cell(cell):
    if '-' in cell.string:
        min_difficulty, max_difficulty = (
            int(s.replace('.', '')) for s in cell.string.split(' - ')
        )
    else:
        min_difficulty = max_difficulty = int(cell.string.replace('.', ''))
    if any(
        difficulty < 10 or difficulty > 99
        for difficulty in (min_difficulty, max_difficulty)
    ):
        raise ValueError(
            'Difficulty {} not between 1.0 and 9.9'.format(cell.string)
        )
    return min_difficulty, max_difficulty


def parse_problem_page(page_soup):
    for row in page_soup.table.tbody.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) != 11:
            raise ValueError('Unexpected number of columns')

        problem_id, problem_name = parse_title_cell(cols[0])
        total_submissions = int(cols[1].string)
        accepted_submissions = int(cols[2].string)
        submissions_ratio = (int(cols[3].string.replace('%', '')) / 100) if '--' not in cols[3].string else None
        fastest_submission = float(cols[4].string) if '--' not in cols[4].string else None
        total_users = int(cols[5].string)
        accepted_users = int(cols[6].string)
        users_ratio = (int(cols[7].string.replace('%', '')) / 100) if '--' not in cols[3].string else None
        min_difficulty, max_difficulty = parse_difficulty_cell(cols[8])

        yield Problem(
            problem_id,
            problem_name,
            total_submissions,
            accepted_submissions,
            submissions_ratio,
            fastest_submission,
            total_users,
            accepted_users,
            users_ratio,
            min_difficulty,
            max_difficulty
        )


def main():
    '''
    Entry point for fetching problems.
    '''
    verbose = '-v' in sys.argv
    with shelve.open('problem_db') as db:
        if '-f' not in sys.argv and time.time() - db.get('_latest_fetch', 0) < 3600:
            raise ValueError('Latest fetch less than an hour old, -f to override')
        problems = {}
        for page_soup in fetch_problem_pages(verbose):
            for problem in parse_problem_page(page_soup):
                if verbose:
                    print(problem)
                problems[problem.problem_id] = problem
            time.sleep(0.5)
        db['problems'] = problems
        db['_latest_fetch'] = time.time()
        db['_by_diff_and_users'] = list(sorted(
            ((p.problem_id, p.min_difficulty, p.total_users) for p in db['problems'].values()),
            key=lambda x: (x[1], -x[2])
        ))


if __name__ == '__main__':
    main()
