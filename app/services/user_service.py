from app.schemas.user import UserInDB
from app.core.security import verify_password, get_password_hash

fake_users_db = {
    "alex": {
        "id": 1,
        "username": "alex",
        "email": "alex@example.com",
        "hashed_password": get_password_hash("secret123"),
        "is_active": True,
    }
}

def get_user_by_username(username: str) -> UserInDB | None:
    """Ищет пользователя по имени"""
    if username in fake_users_db:
        return UserInDB(**fake_users_db[username])
    return None

def authenticate_user(username: str, password: str) -> UserInDB | None:
    """Аутентифицирует пользователя: проверяет, что такой есть и пароль верный"""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user