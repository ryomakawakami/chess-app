from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from sqlalchemy import or_

from models import Matches

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

join_model = match_ns.model('Join', {
    'id': fields.Integer()
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

@match_ns.route('/all')
class MatchesResource(Resource):
    @match_ns.marshal_list_with(match_model)
    @jwt_required()
    def get(self):
        return Matches.query.all()

@match_ns.route('/join')
class MatchesResource(Resource):
    @match_ns.marshal_list_with(match_model)
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        return Matches.query.filter(or_(Matches.status == 'waiting', Matches.status == 'playing'),
            or_(Matches.username1 == user, Matches.username2 == user, Matches.username2 == '')).all()

    @match_ns.expect(join_model)
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

        # TODO: Initialize a new MatchState

        return match
