import jwt
from datetime import datetime, timedelta

from config.config import Config


class TokenUtils:
    @staticmethod
    def generate_token(user_info):
        user_info["exp"] = datetime.utcnow() + timedelta(minutes=1)
        access_token = jwt.encode(user_info, Config.SECRET_KEY, Config.ALGORITHM)

        refresh_data = dict()
        refresh_data["exp"] = datetime.utcnow() + timedelta(minutes=2)
        refresh_token = jwt.encode(refresh_data, Config.SECRET_KEY, Config.ALGORITHM)

        token = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        return token

    @staticmethod
    def validate_token(token):
        try:
            jwt.decode(token, Config.SECRET_KEY, Config.ALGORITHM)
            return True
        except jwt.exceptions.InvalidSignatureError:
            return False

        except jwt.exceptions.ExpiredSignatureError:
            return False
        
        except Exception:
            return False

    @staticmethod
    def get_user(token):
        user_info = jwt.decode(token, Config.SECRET_KEY, Config.ALGORITHM)
        return user_info
