import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
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
        f'*<https://open.kattis.com/problems/{prob.problem_id}|{prob.problem_name}>*'
        f' (Difficulty {diff}, solved by {prob.accepted_users}/{prob.total_users})'
    )


def format_message(selection_date, s_p, m_p, l_p):
    return f'''Problems for {selection_date}:

- :relaxed: {format_problem(s_p)}
- :grimacing: {format_problem(m_p)}
- :scream: {format_problem(l_p)}

GLHF!'''


def main():
    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    try:
        with shelve.open('selected_db', 'r') as selected:
            selection_date = sys.argv[1] if len(sys.argv) > 1 else str(date.today())
            s_p, m_p, l_p = selected[selection_date]
            message_text = format_message(selection_date, s_p, m_p, l_p)
            response = client.chat_postMessage(
                channel='#programming-problems',
                text=message_text
            )
            assert response['message']['text'] == message_text
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
