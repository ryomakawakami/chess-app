import datetime

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from sqlalchemy import or_

from models import Matches, MatchStates, Stats

match_ns = Namespace('match', description='A namespace for matches.')

create_match_model = match_ns.model('CreateMatch', {
    'username2': fields.String()
})

match_model = match_ns.model('Match', {
    'id': fields.Integer(),
    'username1': fields.String(),
    'username2': fields.String(),
    'status': fields.String()
})

id_model = match_ns.model('Id', {
    'id': fields.Integer()
})

match_state_model = match_ns.model('State', {
    'id': fields.Integer(),
    'match_id': fields.Integer(),
    'board': fields.Integer(),
    'turn': fields.Integer(),
    'done': fields.Boolean()
})

@match_ns.route('/create')
class MatchResource(Resource):
    @match_ns.expect(create_match_model)
    @match_ns.marshal_with(match_model)
    @jwt_required()
    def post(self):
        data = request.get_json()
        match = Matches(username1=get_jwt_identity(), username2=data.get('username2'))
        match.save()
        return match, 201

@match_ns.route('/join')
class MatchesResource(Resource):
    @match_ns.marshal_list_with(match_model)
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        return Matches.query.filter(or_(Matches.status == 'waiting', Matches.status == 'playing'),
            or_(Matches.username1 == user, Matches.username2 == user, Matches.username2 == '')).all()

    @match_ns.expect(id_model)
    @match_ns.marshal_with(match_model)
    @jwt_required()
    def post(self):
        user = get_jwt_identity()
        data = request.get_json()

        match = Matches.query.filter_by(id = data.get('id')).first()

        # User can only start matches that they didn't create
        if match.username1 == user:
            return 'error', 400
        if match.username2 == '':
            match.username2 = user
        elif match.username2 != user:
            return 'error', 400
        match.status = 'playing'
        match.save()

        # Initialize a match
        state = MatchStates(match_id=match.id)
        state.save()

        return match

@match_ns.route('/match')
class InMatchResource(Resource):
    @match_ns.marshal_list_with(match_state_model)
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        data = request.get_json()
        id = data.get('id')

        # User must be participating in match
        match = Matches.query.filter_by(id=id).first()
        if user != match.username1 and user != match.username2:
            return 'error', 400

        return MatchStates.query.filter_by(match_id=id).first()

    @match_ns.expect(id_model)  # TODO: Change to a model with ID and the move that the user wants to make
    @match_ns.marshal_with(match_state_model)
    @jwt_required()
    def post(self):
        user = get_jwt_identity()
        data = request.get_json()
        id = data.get('id')
        # move = data.get('move')

        # User must be participating in match
        match = Matches.query.filter_by(id=id).first()
        if user != match.username1 and user != match.username2:
            return 'error', 400

        # Make sure it's their turn
        match_state = MatchStates.query.filter_by(match_id=id).first()
        if user == match.username1 and match_state.turn != 1:
            return 'error', 400
        if user == match.username2 and match_state.turn != 2:
            return 'error', 400

        # Verify move and make move
        # TODO
        match_state.board += 1

        # See if they won
        if match_state.board == 2:  # Temporary win condition
            match_state.done = True

            # Update match object
            match.end = datetime.datetime.now()
            match.winner = match_state.turn
            match.status = 'ended'
            match.save()

            # Update stats
            stats1 = Stats.query.filter_by(username=match.username1).first()
            stats2 = Stats.query.filter_by(username=match.username2).first()
            if match_state.turn == 1:
                stats1.update('win')
                stats2.update('loss')
            else:
                stats1.update('loss')
                stats2.update('win')

        # Next player's turn
        if match_state.turn == 1:
            match_state.turn = 2
        else:
            match_state.turn = 1

        match_state.save()

        return match_state
