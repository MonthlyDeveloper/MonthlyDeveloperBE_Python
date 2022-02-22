from flask import request
from flask_restx import Resource
from flask_restx import fields, Namespace, reqparse
from decorator.token_validator import token_validator
from service.token_service import TokenService

token_ns = Namespace("Token Service", description="토큰 관련 API")

regenerate_token_model = token_ns.model('regenerate token model', {
    'access_token': fields.String(description='Access Token', required=True),
    'refresh_token': fields.String(description='Refresh Token', required=True),
})


@token_ns.route('/regenerate', methods=['POST'])
class RegenerateToken(Resource):
    @token_ns.expect(regenerate_token_model)
    def post(self):

        import jwt
        from config.config import Config

        user_refresh_token = request.json["refresh_token"]
        user_access_token = request.json["access_token"]

        # 두 Token이 모두 만료되지 않았을 때
        try:
            user_info = jwt.decode(user_access_token, Config.SECRET_KEY, Config.ALGORITHM)
            try:
                jwt.decode(user_refresh_token, Config.SECRET_KEY, Config.ALGORITHM)
                user_info.pop("exp")
                return TokenService.generate_token(request, user_info)
            except jwt.exceptions.ExpiredSignatureError:
                return "expired"
            except jwt.exceptions.InvalidSignatureError:
                return "invalid"

        except jwt.exceptions.ExpiredSignatureError:
            user_info = jwt.decode(user_access_token, Config.SECRET_KEY, Config.ALGORITHM,
                                   options={"verify_signature": False})
            try:
                jwt.decode(user_refresh_token, Config.SECRET_KEY, Config.ALGORITHM)
                user_info.pop("exp")
                return TokenService.generate_token(request, user_info)
            except jwt.exceptions.ExpiredSignatureError:
                return "both token expired"
            except jwt.exceptions.InvalidSignatureError:
                return "invalid"

        except jwt.exceptions.InvalidSignatureError:
            return "invalid"

        except Exception:
            return "unknown error"
