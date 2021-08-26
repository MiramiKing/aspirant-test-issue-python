import requests

WEATHER_API_KEY = '99ba78ee79a2a24bc507362c5288a81b'


class GetWeatherRequest:
    """
    Выполняет запрос на получение текущей погоды для города
    """

    def __init__(self):
        """
        Инициализирует класс
        """
        self.session = requests.Session()

    def get_weather_url(self, city):
        """
        Генерирует url включая в него необходимые параметры
        Args:
            city: Город
        Returns:

        """
        url = ('https://api.openweathermap.org/data/2.5/weather'
               f'?units=metric&q={city}&appid={WEATHER_API_KEY}')
        return url

    def send_request(self, url, check=False):
        """
        Отправляет запрос на сервер
        Args:
            url: Адрес запроса
        Returns:

        """
        if check:
            r = self.session.get(url)
            return r

        r = self.session.get(url)
        if r.status_code != 200:
            r.raise_for_status()
        return r

    def get_weather_from_response(self, response):
        """
        Достает погоду из ответа
        Args:
            response: Ответ, пришедший с сервера
        Returns:

        """
        data = response.json()
        return data['main']['temp']

    def get_weather(self, city):
        """
        Делает запрос на получение погоды
        Args:
            city: Город
        Returns:

        """
        url = self.get_weather_url(city)
        r = self.send_request(url)
        if r is None:
            return None
        else:
            weather = self.get_weather_from_response(r)
            return weather

    def check_existing(self, city):
        """
        Проверяет наличие города
        Args:
            city: Название города
        Returns:

        """
        url = self.get_weather_url(city)
        r = self.send_request(url, check=True)
        if r.status_code == 404:
            return False
        if r.status_code == 200:
            return True
