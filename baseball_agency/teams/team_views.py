from flask import Blueprint, jsonify, request, abort

from .. import app
from ..models import Player, Team

teams = Blueprint('teams', __name__)

TEAMS_PER_PAGE = 10


def paginate_players(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * TEAMS_PER_PAGE
    end = start + TEAMS_PER_PAGE

    teams = [team.format() for team in selection]
    current_teams = teams[start:end]

    return current_teams


@teams.route('/teams', methods=['GET'])
def get_all_teams():
    try:
        team_query = Team.query.all()

        all_teams = [team.format() for team in team_query]

        return jsonify({
            'success': True,
            'teams': all_teams
        }), 200

    except Exception as error:
        raise error
