from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from models import Stats

stats_ns = Namespace('stats', description='A namespace for stats.')

stats_model = stats_ns.model('Stats', {
    'id': fields.Integer(),
    'username': fields.String(),
    'wins': fields.Integer(),
    'losses': fields.Integer(),
    'draws': fields.Integer()
})

@stats_ns.route('/stats')
class StatsResource(Resource):
    @stats_ns.marshal_list_with(stats_model)
    @jwt_required()
    def get(self):
        return Stats.query.filter_by(username=get_jwt_identity()).first(), 200
