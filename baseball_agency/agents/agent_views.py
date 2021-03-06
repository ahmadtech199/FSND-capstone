import json

from flask import jsonify, request, abort
from sqlalchemy.exc import IntegrityError

from auth.auth import requires_auth
from baseball_agency.agents import agents_bp
from .helpers import valid_agent_body, valid_agent_patch_body
from ..models import Player, Agent


@agents_bp.route('/agents', methods=['GET'])
@requires_auth('get:agents')
def get_all_agents(jwt):
    try:
        agents_query = Agent.query.all()

        if not agents_query:
            abort(404)

        all_agents = [agent.format() for agent in agents_query]

        return jsonify({
            'success': True,
            'agents': all_agents,
            'total_agents': len(all_agents)
        }), 200

    except Exception as error:
        raise error


@agents_bp.route('/agents/<int:agent_id>/details', methods=['GET'])
@requires_auth('get:agent-details')
def get_specific_agent_details(jwt, agent_id):
    try:
        agent = Agent.query.filter_by(id=agent_id).first_or_404()

        return jsonify({
            'success': True,
            'agent': agent.format_extended()
        }), 200

    except Exception as error:
        raise error


@agents_bp.route('/agents/<int:agent_id>/clients', methods=['GET'])
@requires_auth('get:agent-clients')
def get_agent_clients(jwt, agent_id):
    try:
        agent = Agent.query.filter_by(id=agent_id).first_or_404()

        client_query = Player.query.filter_by(agent_id=agent.id).all()
        if not client_query:
            abort(404)

        clients = [player.format() for player in client_query]

        return jsonify({
            'success': True,
            'agent': agent.name,
            'clients': clients,
            'total_agent_clients': len(clients)
        }), 200

    except Exception as error:
        raise error


@agents_bp.route('/agents', methods=['POST'])
@requires_auth('post:agents')
def post_agent(jwt):
    try:
        body = json.loads(request.data)

        if not valid_agent_body(body):
            abort(400)

        new_agent = Agent(**body)
        new_agent.insert()

        return jsonify({
            'success': True,
            'new_agent_id': new_agent.id,
            'new_agent': new_agent.format_extended(),
            'total_agents': len(Agent.query.all())
        }), 201

    except json.decoder.JSONDecodeError:
        abort(400)
    except TypeError:
        abort(400)
    except Exception as error:
        raise error


@agents_bp.route('/agents/<int:agent_id>', methods=['DELETE'])
@requires_auth('delete:agents')
def delete_agent(jwt, agent_id):
    try:
        agent = Agent.query.filter_by(id=agent_id).first_or_404()

        """First query players assigned to agent in case of IntegrityError,
        so that the error return function can display players assigned to
        agent, since an agent cannot be deleted if it has players assigned to
        it."""
        player_query = Player.query.filter(Player.agent_id == agent.id)
        client_list = [(f'id: {client.id}', f'name: {client.name}') for client
                       in player_query]

        agent.delete()

        return jsonify({
            'success': True,
            'deleted_id': agent.id,
            'total_agents': len(Agent.query.all())
        }), 200

    except IntegrityError:
        return jsonify({
            'success': False,
            'message': 'This agent currently represents one or more players. '
                       'Please reassign those players before deleting this '
                       'agent!',
            'clients': client_list,
            'total_clients': len(client_list)
        }), 400
    except Exception as error:
        raise error


@agents_bp.route('/agents/<int:agent_id>', methods=['PATCH'])
@requires_auth('patch:agents')
def patch_agent_details(jwt, agent_id):
    try:
        agent = Agent.query.filter_by(id=agent_id).first_or_404()

        body = request.get_json()

        if not valid_agent_patch_body(body):
            abort(400)

        for k, v in body.items():
            setattr(agent, k, v)

        agent.update()

        return jsonify({
            'success': True,
            'updated_agent': agent.format_extended()
        }), 200

    except Exception as error:
        raise error
