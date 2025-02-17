from flask import Blueprint, render_template

game = Blueprint('balloons', __name__)


@game.route('/globos')
def index():
    return render_template('games.html')

