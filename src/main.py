import datetime as dt

from fastapi import FastAPI, HTTPException, Query

from database import Session, City, User, Picnic, PicnicRegistration
from external_requests import GetWeatherRequest
from models import RegisterUserRequest, UserModel

app = FastAPI()


@app.get('/create-city/', summary='Create City',
         description='Создание города по его названию')
def create_city(city: str = Query(description="Название города", default=None)):
    """
    Добавление нового города, если он присутсвует в сервисе погоды
    """
    if city is None:
        raise HTTPException(
            status_code=400, detail='Параметр city должен быть указан'
        )
    check = GetWeatherRequest()
    if not check.check_existing(city):
        raise HTTPException(
            status_code=400,
            detail='Параметр city должен быть существующим городом'
        )

    city_object = Session().query(City).filter(
        City.name == city.capitalize()
    ).first()
    if city_object is None:
        city_object = City(name=city.capitalize())
        s = Session()
        s.add(city_object)
        s.commit()

    return {
        'id': city_object.id,
        'name': city_object.name,
        'weather': city_object.weather
    }


@app.post('/get-cities/', summary='Get Cities')
def cities_list(q: str = Query(description="Название города", default=None)):
    """
    Получение списка городов
    """
    cities = Session().query(City).all()
    if q:
        city = Session().query(City).filter(City.name == q.title()).first()
        if city:
            return {'id': city.id, 'name': city.name, 'weather': city.weather}

    return [{
        'id': city.id, 'name': city.name, 'weather': city.weather
    } for city in cities]


@app.post('/users-list/', summary='Get users')
def users_list(
        min_age: int = Query(description="Минимальный возраст", default=None),
        max_age: int = Query(description="Максимальный возраст", default=None)
):
    """
    Список пользователей
    """
    users = Session().query(User).all()
    if min_age:
        users = Session().query(User).filter(User.age > min_age)
    if max_age:
        users = Session().query(User).filter(User.age < max_age)
    return [{
        'id': user.id,
        'name': user.name,
        'surname': user.surname,
        'age': user.age,
    } for user in users]


@app.post('/register-user/', summary='CreateUser', response_model=UserModel)
def register_user(user: RegisterUserRequest):
    """
    Регистрация пользователя
    """
    user_object = User(**user.dict())
    s = Session()
    s.add(user_object)
    s.commit()

    return UserModel.from_orm(user_object)


@app.get('/all-picnics/', summary='All Picnics', tags=['picnic'])
def all_picnics(
        datetime: dt.datetime = Query(
            default=None, description='Время пикника (по умолчанию не задано)'
        ),
        past: bool = Query(
            default=True, description='Включая уже прошедшие пикники'
        )):
    """
    Список всех пикников
    """
    picnics = Session().query(Picnic)
    if datetime:
        picnics = picnics.filter(Picnic.time == datetime)
    if not past:
        picnics = picnics.filter(Picnic.time >= dt.datetime.now())

    return [{
        'id': pic.id,
        'city': Session().query(City).filter(
            City.id == pic.city_id
        ).first().name,
        'time': pic.time,
        'users': [
            {
                'id': picnic.user.id,
                'name': picnic.user.name,
                'surname': picnic.user.surname,
                'age': picnic.user.age,
            }
            for picnic in pic.users],
    } for pic in picnics]


@app.get('/picnic-add/', summary='Picnic Add', tags=['picnic'])
def picnic_add(city_id: int = ..., datetime: dt.datetime = ...):
    if datetime < dt.datetime.now():
        return {'error': 'Необходимо ввести будущую дату'}
    p = Picnic(city_id=city_id, time=datetime)
    s = Session()
    s.add(p)
    s.commit()

    return {
        'id': p.id,
        'city': Session().query(City).filter(
            City.id == p.city_id
        ).first().name,
        'time': p.time,
    }


@app.get('/picnic-register/', summary='Picnic Registration', tags=['picnic'])
def register_to_picnic(
        user_id: int = Query(..., description="Идентификатор пользователя"),
        picnic_id: int = Query(..., description="Идентификатор пикника"),
):
    """
    Регистрация пользователя на пикник
    """
    new_picnic = PicnicRegistration(user_id=user_id, picnic_id=picnic_id)
    session = Session()
    session.add(new_picnic)
    session.commit()
    picnic_obj = Session().query(Picnic).filter(Picnic.id == picnic_id).first()
    return {
        'id': picnic_obj.id,
        'city': Session().query(City).filter(
            City.id == picnic_obj.city_id
        ).first().name,
        'time': picnic_obj.time,
        'users': [
            {
                'id': picnic.user.id,
                'name': picnic.user.name,
                'surname': picnic.user.surname,
                'age': picnic.user.age,
            }
            for picnic in picnic_obj.users],
    }
