import os
import sys
import shelve
from datetime import date
from pprint import pprint


def format_problem(prob):
    diff = (
        f'{prob.min_difficulty/10:.1f}'
        if prob.min_difficulty == prob.max_difficulty
        else f'{prob.min_difficulty/10:.1f} - {prob.max_difficulty/10:.1f}'
    )
    return (
        f'<b><a href="https://open.kattis.com/problems/{prob.problem_id}">{prob.problem_name}</a></b>'
        f' (Difficulty {diff}, solved by {prob.accepted_users}/{prob.total_users})'
    )


def format_message(selection_date, s_p, m_p, l_p):
    return f'''<h1>Problems for {selection_date}</h1>

<ul>
<li>☺️ {format_problem(s_p)}</li>
<li>😬 {format_problem(m_p)}</li>
<li>😱 {format_problem(l_p)}</li>
</ul>

<p>GLHF!</p>'''


def main():
    html_string = open('template.html').read()
    with shelve.open('selected_db', 'r') as selected:
        selection_date = sys.argv[1] if len(sys.argv) > 1 else str(date.today())
        s_p, m_p, l_p = selected[selection_date]
        message_text = format_message(selection_date, s_p, m_p, l_p)
        sys.stdout.write(html_string.replace('PROBLEM_TEXT', message_text))


if __name__ == '__main__':
    main()
