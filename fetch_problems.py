#!/Users/kalle/venv/kattisscraping/bin/python

import sys
import time
import requests
from bs4 import BeautifulSoup

KATTIS_SERVER = 'https://open.kattis.com'
PROBLEM_LIST_PATH = '/problems'
REQUEST_HEADERS = {
    'User-Agent': 'KattisArchiveBot/0.0 (kalle@scharlund.se)',
}


class Problem:
    def __init__(self,
                 problem_id,
                 problem_name,
                 total_submissions,
                 accepted_submissions,
                 submissions_ratio,
                 fastest_submission,
                 total_users,
                 accepted_users,
                 users_ratio,
                 difficulty):
        self.problem_id = problem_id
        self.problem_name = problem_name
        self.total_submissions = total_submissions
        self.accepted_submissions = accepted_submissions
        self.submissions_ratio = submissions_ratio
        self.fastest_submission = fastest_submission
        self.total_users = total_users
        self.accepted_users = accepted_users
        self.users_ratio = users_ratio
        self.difficulty = difficulty

    def __str__(self):
        return ' '.join((self.problem_id, self.problem_name))


def fetch_problem_pages():
    page_path = PROBLEM_LIST_PATH
    while page_path:
        print('Fetching', KATTIS_SERVER + page_path, file=sys.stderr)
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
        raise ValueError('Expected a name column first. Has the format changed?')
    link = cell.a['href']
    link_elements = link.split('/')
    if len(link_elements) != 3 or link_elements[0] or link_elements[1] != 'problems':
        raise ValueError('Unexpected problem link format ' + link)
    problem_id = link_elements[-1]
    problem_name = cell.string
    return problem_id, problem_name


def parse_problem_page(page_soup):
    for row in page_soup.table.tbody.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) != 11:
            raise ValueError('Unexpected number of columns')

        problem_id, problem_name = parse_title_cell(cols[0])
        total_submissions = int(cols[1].string)
        accepted_submissions = int(cols[2].string)
        submissions_ratio = int(cols[3].string.replace('%', '')) / 100
        fastest_submission = float(cols[4].string)
        total_users = int(cols[5].string)
        accepted_users = int(cols[6].string)
        users_ratio = int(cols[7].string.replace('%', '')) / 100
        difficulty = int(cols[8].string.replace('.', ''))
        if difficulty < 10 or difficulty > 99:
            raise ValueError('Difficulty {} not between 1.0 and 9.9'.format(difficulty))

        yield Problem(problem_id, problem_name, total_submissions, accepted_submissions, submissions_ratio, fastest_submission, total_users, accepted_users, users_ratio, difficulty)


def main():
    '''
    Entry point for fetching problems.
    '''
    for page_soup in fetch_problem_pages():
        for problem in parse_problem_page(page_soup):
            print(problem)
        time.sleep(1)


if __name__ == '__main__':
    main()
