import sys
from io import BytesIO  # Этот класс поможет нам сделать картинку из потока байт
from size_found import found_size_function
import requests
from PIL import Image

# Пусть наше приложение предполагает запуск:
# python search.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:
try:
    toponym_to_find = " ".join(sys.argv[1:])
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "07901535-640b-47f1-b95e-4b7055de1924",
        "geocode": toponym_to_find,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        # обработка ошибочной ситуации
        pass

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    delta = found_size_function(toponym)
    apikey = "18cf6f36-a87a-4b02-829a-91c5ba3be0ec"

    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": ",".join(delta),
        "apikey": apikey,
        "pt": f'{",".join([toponym_longitude, toponym_lattitude])},round'
    }

    map_api_server = "https://static-maps.yandex.ru/v1"
    # ... и выполняем запрос

    response = requests.get(map_api_server, params=map_params)
    im = BytesIO(response.content)
    opened_image = Image.open(im)
    opened_image.show()  # Создадим картинку и тут же ее покажем встроенным просмотрщиком операционной системы
except Exception as error:
    print(error)
