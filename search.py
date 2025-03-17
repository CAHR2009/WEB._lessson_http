import sys
from io import BytesIO
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
    organizations = json_response["features"]
    max_longitude = 0
    max_lattitude = 0
    min_longitude = 9999999
    min_lattitude = 9999999
    spic = []
    color = ''
    for i in organizations:
        # Получаем координаты ответа.
        point = i["geometry"]["coordinates"]
        org_point = f"{point[0]},{point[1]}"
        if float(point[0]) > max_longitude:
            max_longitude = point[0]
        elif float(point[0]) < min_longitude:
            min_longitude = point[0]
        if float(point[1]) > max_lattitude:
            max_lattitude = point[1]
        elif float(point[1]) < min_lattitude:
            min_lattitude = point[1]
        try:
            if "TwentyFourHours" in i["properties"]["CompanyMetaData"]["Hours"]["Availabilities"][0]:
                color = 'gn'
            elif "Intervals" in i["properties"]["CompanyMetaData"]["Hours"]["Availabilities"][0]:
                color = 'bl'
        except Exception as error:
            color = 'gr'
        spic.append(f'{org_point},pm{color}s')
    org_point = f"{max_longitude},{max_lattitude}"
    apikey = "18cf6f36-a87a-4b02-829a-91c5ba3be0ec"
    pt_stroka = '~'.join(spic) + f'~{toponym_longitude},{toponym_lattitude},comma'
    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        # позиционируем карту центром на наш исходный адрес
        "ll": f'{toponym_longitude},{toponym_lattitude}',
        "bbox": f'{min_longitude},{min_lattitude}~{org_point}',
        "apikey": apikey,
        "pt": pt_stroka
    }
    map_api_server = "https://static-maps.yandex.ru/v1"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)
    im = BytesIO(response.content)
    opened_image = Image.open(im)
    font = ImageFont.truetype("arial.ttf", size=20)
    opened_image.show()

except Exception as error:
    print(error)