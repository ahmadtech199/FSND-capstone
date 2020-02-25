import json

from flask import Blueprint, jsonify, request, abort
from sqlalchemy.exc import IntegrityError

from .. import app
from ..models import Player, Team
from .helpers import valid_team_body

teams = Blueprint('teams', __name__)

TEAMS_PER_PAGE = 10


def paginate_teams(request, selection):
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

        all_teams = [team.team_name for team in team_query]

        return jsonify({
            'success': True,
            'teams': all_teams
        }), 200

    except Exception as error:
        raise error


@teams.route('/teams/<int:team_id>', methods=['GET'])
def get_specific_team_details(team_id):
    # will require authentication level 1
    try:
        team = Team.query.filter(Team.id == team_id).first_or_404()

        if team is None:
            abort(404)

        return jsonify({
            'success': True,
            'team_details': team.format(),
            'total_teams': len(Team.query.all())
        }), 200

    except Exception as error:
        raise error


@teams.route('/teams', methods=['POST'])
def add_team():
    # will require authentication level 2
    try:
        body = json.loads(request.data)

        if not valid_team_body(body):
            abort(422)

        new_team = Team(**body)
        new_team.insert()

        current_teams = paginate_teams(request,
                                       Team.query.order_by(Team.id).all())

        return jsonify({
            'success': True,
            'new_team_id': new_team.id,
            'new_team': new_team.format(),
            'teams': current_teams,
            'total_teams': len(Team.query.all())
        }), 201

    except json.decoder.JSONDecodeError:
        abort(400)
    except Exception as error:
        raise error


@teams.route('/teams/<int:team_id>', methods=['DELETE'])
def delete_team(team_id):
    # will require authentication level 3
    try:
        team = Team.query.filter(Team.id == team_id).one_or_none()

        if team is None:
            abort(404)

        player_query = Player.query.filter(Player.team_id == team.id)
        team_roster = [(player.id, player.name) for player in player_query]

        team.delete()

        return jsonify({
            'success': True,
            'deleted_id': team.id,
            'total_teams': len(Team.query.all())
        }), 200

    except IntegrityError:
        return jsonify({
            'success': False,
            'message': 'This team currently has one or more players. Please '
                       'reassign those players before deleting this team!',
            'players': team_roster,
            'total_players': len(team_roster)
        })
    except Exception as error:
        raise error
