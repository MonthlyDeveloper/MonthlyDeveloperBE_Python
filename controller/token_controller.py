from flask import request
from flask_restx import Resource
from flask_restx import fields, Namespace, reqparse
from decorator.token_validator import token_validator

token_ns = Namespace("Token Service", description="토큰 관련 API")

regenerate_token_model = token_ns.model('regenerate token model', {
    'access_token': fields.String(description='Access Token', required=True),
    'refresh_token': fields.String(description='Refresh Token', required=True),
})

@token_ns.route('/regenerate', methods=['POST'])
class RegenerateToken(Resource):
    @token_validator
    @token_ns.expect(regenerate_token_model)
    def post(self):
        print(request.json)
