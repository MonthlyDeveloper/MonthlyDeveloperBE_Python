from flask import request
from flask_restx import Resource
from flask_restx import fields, Namespace, reqparse
from service.token_utils import TokenUtils

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
        from model.response_model import ResponseModel

        user_refresh_token = request.json["refresh_token"]
        user_access_token = request.json["access_token"]

        # 두 Token이 모두 만료되지 않았을 때
        try:
            user_info = jwt.decode(user_access_token, Config.SECRET_KEY, Config.ALGORITHM)
            # 이후 Refresh Token이 유효한지 확인
            # Refresh Token이 유효하다면 토큰 재발급
            try:
                jwt.decode(user_refresh_token, Config.SECRET_KEY, Config.ALGORITHM)
                user_info.pop("exp")
                return TokenUtils.generate_token(request, user_info)
            except jwt.exceptions.ExpiredSignatureError:
                return ResponseModel.set_response(request.path, 200, "Refresh Token Expired", None)
            except jwt.exceptions.InvalidSignatureError:
                return ResponseModel.set_response(request.path, 200, "Invalid Refresh Token", None)

        # Access Token이 만료 되었을 때
        except jwt.exceptions.ExpiredSignatureError:
            # Token에서 사용자 정보를 가져옴
            user_info = jwt.decode(user_access_token, Config.SECRET_KEY, Config.ALGORITHM,
                                   options={"verify_signature": False})
            # 이후 Refresh Token이 유효한지 확인
            # Refresh Token 이라도 유효하다면 토큰 재발급
            try:
                jwt.decode(user_refresh_token, Config.SECRET_KEY, Config.ALGORITHM)
                user_info.pop("exp")
                return TokenUtils.generate_token(user_info)
            # 유효하지 않다면 재발급 실패
            except jwt.exceptions.ExpiredSignatureError:
                return ResponseModel.set_response(request.path, 200, "Refresh Token Expired", None)
            except jwt.exceptions.InvalidSignatureError:
                return ResponseModel.set_response(request.path, 200, "Invalid Refresh Token", None)

        except jwt.exceptions.InvalidSignatureError:
            return ResponseModel.set_response(request.path, 200, "Invalid Access Token", None)

        except Exception:
            return ResponseModel.set_response(request.path, 200, "Token Error", None)
