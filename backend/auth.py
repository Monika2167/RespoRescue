from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.models import User


# Password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str
):
    # Check whether username already exists
    existing_username = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_username:
        return None, "Username already exists"

    # Check whether email already exists
    existing_email = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_email:
        return None, "Email already exists"

    # Hash password before storing
    hashed_password = hash_password(password)

    user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user, None