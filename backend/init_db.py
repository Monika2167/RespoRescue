from backend.database import engine, Base
from backend.models import User, Repository, Analysis


def init_database():
    Base.metadata.create_all(bind=engine)
    print("RepoRescue database created successfully!")
    print("Tables created: users, repositories, analyses")


if __name__ == "__main__":
    init_database()