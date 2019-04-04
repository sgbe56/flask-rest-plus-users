import pytest

from app import app, db
from app.models.Keys import Keys
from app.models.Users import Users
from tests.TestRegistration import TestRegistration
from tests.TestUser import TestUser
from tests.TestRestorePassword import TestRestorePassword


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        db.create_tables([Users, Keys])
    yield client
