from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
import jwt

router = APIRouter()

class JWTHandler:
    SECRET_KEY = "secreeeeet"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS = 15/60  
    REFRESH_TOKEN_EXPIRE_DAY = 30

    @staticmethod
    def create_jwt_token(email: str) -> str:
        payload = {
            "sub": email,
            "exp": datetime.now(tz=timezone.utc) + timedelta(hours=JWTHandler.ACCESS_TOKEN_EXPIRE_HOURS),
            "type": "access"
        }
        token = jwt.encode(payload, JWTHandler.SECRET_KEY, algorithm=JWTHandler.ALGORITHM)
        return token

    @staticmethod
    def create_refresh_token(email: str) -> str:
        expire_delta = timedelta(days=JWTHandler.REFRESH_TOKEN_EXPIRE_DAY)
        payload = {
            "sub": email,
            "exp": datetime.now(tz=timezone.utc) + expire_delta,
            "type": "refresh"
        }
        token = jwt.encode(payload, JWTHandler.SECRET_KEY, algorithm=JWTHandler.ALGORITHM)
        return token

    @staticmethod
    def update_jwt_payload(token: str, new_data: dict) -> str:
        try:
            payload = jwt.decode(token, JWTHandler.SECRET_KEY, algorithms=[JWTHandler.ALGORITHM])
            if "booking" in new_data:
                payload["booking"] = new_data["booking"]

            payload["exp"] = datetime.now(tz=timezone.utc) + timedelta(hours=168)
            updated_token = jwt.encode(payload, JWTHandler.SECRET_KEY, algorithm=JWTHandler.ALGORITHM)
            print(f"JWT更新 form update_jwt_payload")

            return updated_token

        except jwt.PyJWTError as exception:
            print(f"JWT Error: {exception}")
            return None

    @staticmethod
    def remove_booking_from_jwt(token: str) -> str:
        try:
            payload = jwt.decode(token, JWTHandler.SECRET_KEY, algorithms=[JWTHandler.ALGORITHM])
            del payload["booking"]
            payload["exp"] = datetime.now(tz=timezone.utc) + timedelta(hours=168)
            updated_token = jwt.encode(payload, JWTHandler.SECRET_KEY, algorithm=JWTHandler.ALGORITHM)
            print(f"JWT 已更新，booking 已移除 from remove_booking_from_jwt")
            return updated_token

        except jwt.PyJWTError as exception:
            print(f"JWT Error: {exception}")
            return None
    
    @staticmethod
    def confirm_same_user_by_jwt(token: str, user_email: str) -> bool:
        payload = jwt.decode(token, JWTHandler.SECRET_KEY, algorithms=[JWTHandler.ALGORITHM])
        payload["sub"] = user_email
        return True
    
    @staticmethod
    def get_user_email(token: str):
        try:
            payload = jwt.decode(token, JWTHandler.SECRET_KEY, algorithms=[JWTHandler.ALGORITHM])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            return None
        except jwt.PyJWTError:
            return None

    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, JWTHandler.SECRET_KEY, algorithms=[JWTHandler.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.PyJWTError:
            return None

    @staticmethod
    def is_token_expired(token: str) -> bool:
        try:
            jwt.decode(token, JWTHandler.SECRET_KEY, algorithms=[JWTHandler.ALGORITHM])
            return False
        except jwt.ExpiredSignatureError:
            return True
        except jwt.PyJWTError:
            return True
        
    