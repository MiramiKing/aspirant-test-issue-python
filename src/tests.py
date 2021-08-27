from fastapi.testclient import TestClient

from main import app

test_client = TestClient(app)


def test_user_registration():
    name, surname, age = "John", "Johnov", 22
    test_json = {"name": name, "surname": surname, "age": age}

    response = test_client.post('/register-user/', json=test_json)
    assert response.status_code == 200
    assert response.json()['name'] == name
    assert response.json()['surname'] == surname
    assert response.json()['age'] == age


def test_success_city_creation():
    city = "New york"
    params = {"city": city}

    response = test_client.get('/create-city/', params=params)
    assert response.status_code == 200
    assert response.json()['name'] == city


def test_fail_city_creation():
    city = "trqrqoiioadoji"
    params = {"city": city}
    fail_message = 'Параметр city должен быть существующим городом'

    response = test_client.get('/create-city/', params=params)
    assert response.status_code == 400
    assert response.json()['detail'] == fail_message

