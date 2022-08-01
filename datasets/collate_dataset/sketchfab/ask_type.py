import json
import requests
from requests.exceptions import RequestException

url = 'https://api.sketchfab.com/v3/categories'
try:
    response = requests.get(url)
except RequestException as exc:
    print(f'An API error occured: {exc}')
else:
    data = response.json()
    result = data['results']
    assert(data['next'] is None)
    with open('type.json', 'w') as file:
        file.write(json.dumps(result))