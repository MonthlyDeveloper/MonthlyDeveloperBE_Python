import requests

from config.config import Config
from config.connector import Connector

from service.github.github_request import GithubRequest


class LoginService:

    # DB 연결에 필요한 설정
    def __init__(self) -> None:
        self.mongodb_connector = Connector.mongodb_connector()
        self.counter_db = self.mongodb_connector.counter
        self.user_db = self.mongodb_connector.users

    @staticmethod
    def get_github_user_info(access_code):
        access_token = GithubRequest.request_access_token(access_code)
        user_info = GithubRequest.request_user_info(access_token)
        return user_info

    """
        로그인한 사람이 사용자(서비스 이용자)인지 확인하는 함수
    """
    def is_existing_user(self, github_user_info):
        user_info = self.user_db.find_one({"github_id": str(github_user_info.id)}, {"_id": 0})
        
        if user_info is not None:
            if user_info["login"] == str(github_user_info.login) and user_info["email"] == str(github_user_info.email):
                return user_info
        else:
            return False

    def refresh_existing_user_token(self, github_id, refresh_token):
        self.user_db.update_one({"github_id": github_id}, {"$set": {"token": refresh_token}})
        return True

    def save_user(self, user_info, refresh_token):
        # 서비스에서 고객의 ID는 순차적으로 부여함
        user_id = self.counter_db.find_one({"type": "users"}, {"_id": 0})["counter"] + 1

        db_users = Connector.mongodb_connector().users
        try:
            user_info = {   
                "id": user_id,
                "github_id": str(user_info.id),
                "login": str(user_info.login),
                "email": str(user_info.email),
                "approval": True,
                "role": "user",
                "token": refresh_token
            }
            db_users.insert_one(user_info)
            self.counter_db.update_one({"type": "users"}, {"$set": {"counter": user_id}})
            return True
        except:
            return False
