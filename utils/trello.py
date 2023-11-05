from flask import current_app
from database import User
import requests
import json
import datetime


def createTrelloBoards(user):
    board = current_app.config['trelloClient'].add_board(
        board_name=user.username + " board",
        default_lists=False,
    )
    list1 = board.add_list(name='In progress', pos='bottom')
    time_24_hours_later = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    dueDate = time_24_hours_later.strftime("%Y-%m-%dT%H:%M:%SZ")
    list1.add_card(name='First post', due=dueDate)
    board.add_list(name='Delivered', pos='bottom')
    board.add_list(name='In revision', pos='bottom')
    board.add_list(name='Completed', pos='bottom')
    inviteToJoin(user, board)
    updateUser = User.query.filter_by(username=user.username).first()
    updateUser.trello = board.url
    current_app.config['database'].session.commit()


def inviteToJoin(user, board):
    url = 'https://api.trello.com/1/boards/' + board.id + '/members'
    headers = {
        "Content-Type": "application/json"
    }
    query = {
        'email': user.email,
        'key':  current_app.config["TRELLO_KEY"],
        'token':  current_app.config["TRELLO_TOKEN"]
    }
    payload = json.dumps({
        "fullName": user.username
    })
    response = requests.request(
        "PUT",
        url,
        data=payload,
        headers=headers,
        params=query
    )
    return response.status_code
