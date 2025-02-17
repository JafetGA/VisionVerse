from flask import Blueprint, render_template

main = Blueprint('main', __name__)
game = Blueprint('game', __name__)
api = Blueprint('api', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@game.route('/games')
def games():
    return render_template('games.html')