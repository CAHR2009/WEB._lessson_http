import sys
from io import BytesIO  # Этот класс поможет нам сделать картинку из потока байт
from size_found import found_size_function
import requests
from PIL import Image, ImageDraw, ImageFont

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

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    search_params = {
        "apikey": api_key,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": f'{toponym_longitude}, {toponym_lattitude}',
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    json_response = response.json()

    # Получаем первую найденную организацию.
    organization = json_response["features"][0]

    # Получаем координаты ответа.
    point = organization["geometry"]["coordinates"]
    org_point = f"{point[0]},{point[1]}"
    apikey = "18cf6f36-a87a-4b02-829a-91c5ba3be0ec"

    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        # позиционируем карту центром на наш исходный адрес
        "ll": f'{toponym_longitude},{toponym_lattitude}',
        "bbox": f'{toponym_longitude},{toponym_lattitude}~{org_point}',
        "apikey": apikey,
        "pt": f"{toponym_longitude},{toponym_lattitude},comma~{org_point},org"
    }
    map_api_server = "https://static-maps.yandex.ru/v1"
    # ... и выполняем запрос
    rastoyanie = found_size_function(toponym_longitude, toponym_lattitude, org_point)
    response = requests.get(map_api_server, params=map_params)
    snipet = [rastoyanie + 'м', organization["properties"]["CompanyMetaData"]["address"],
              organization["properties"]["CompanyMetaData"]["name"],
              organization["properties"]["CompanyMetaData"]["Hours"]["text"]]
    im = BytesIO(response.content)
    opened_image = Image.open(im)
    font = ImageFont.truetype("arial.ttf", size=20)
    idraw = ImageDraw.Draw(opened_image)
    y = 10
    for i in snipet:
        y += 20
        idraw.text((155, y), i, font=font, fill=(255, 0, 0))
    opened_image.show()

except Exception as error:
    print(error)
