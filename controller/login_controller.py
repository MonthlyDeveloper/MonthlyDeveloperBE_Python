from tokenize import Token
from config.config import Config

from flask import url_for, redirect, request
from flask_restx import Resource, Namespace

from model.login_model import LoginModel

from service.login_service import LoginService
from service.token_utils import TokenUtils

from model.response_model import ResponseModel

"""
Authlib을 사용하지 않고 구현
로그인 URL: ~/login/github
"""
login_ns = LoginModel.login_ns
github_callback_parser = LoginModel.github_callback_parser

# 로그인과 관련된 서비스 초기화
login_service = LoginService()


# 사용자가 로그인 할 때 접속하는 URL (http://localhost:5000/login/github)
@login_ns.route('/github', methods=['GET'], doc=False)
class Github(Resource):
    @login_ns.expect()
    def get(self):
        # Github 측으로 로그인하고 Access Code를 받기 위해 redirect 설정
        redirect_uri = f"http://github.com/login/oauth/authorize?client_id={Config.GITHUB_CLIENT_ID}&redirect_uri={Config.REDIRECT_URL}"
        # 로그인을 위한 redirect
        return redirect(redirect_uri)


# Access Code를 전달받기 위한 URL (http://localhost:5500/login/callback)
@login_ns.route('/callback', methods=['GET'])
class GithubCallback(Resource):
    @login_ns.expect(github_callback_parser)
    def get(self):
        # callback으로 내려온 access code를 저장
        access_code = request.args["code"]

        # 전달받은 access code를 토대로 사용자 정보 요청
        github_user_info = login_service.get_github_user_info(access_code)
        
        # 로그인을 시도한 사람이 사용자(서비스 이용자)인지 확인
        user_info = login_service.is_existing_user(github_user_info)
        
        if isinstance(user_info, dict):
            print("Already")
            token_set = TokenUtils.generate_token(user_info)
            login_service.refresh_existing_user_token(user_info["github_id"], token_set["refresh_token"])
            return ResponseModel.set_response(request.path, 200, "Already User", token_set)
        else:
            print("New")
            token_set = TokenUtils.generate_token(github_user_info.toDict())
            login_service.save_user(github_user_info, token_set["refresh_token"])
            return ResponseModel.set_response(request.path, 200, "New User", token_set)
