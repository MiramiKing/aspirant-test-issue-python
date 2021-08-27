import pytest

from fastapi import testclient


class DB:
    def __init__(self):
        self.intransaction = []

    def append(self, name):
        self.intransaction.append(name)

    def pop(self):
        self.intransaction.pop()


@pytest.fixture
def db():
    from src.database import User
    return DB()


@pytest.fixture
def create_user():
    db = DB()
    pass
    # return db.append(name)


@pytest.fixture
def transact(request, db):
    db.begin()
    yield
    db.rollback()