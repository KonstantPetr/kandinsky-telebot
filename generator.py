import os
import time
import json
import base64
import requests
from dotenv import find_dotenv, load_dotenv


class Text2ImageAPI:
    def __init__(self, url, secret_key, api_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Secret': f'Secret {secret_key}',
            'X-Key': f'Key {api_key}'
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024, style='DEFAULT'):
        params = {
            "type": "GENERATE",
            'style': style,
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']
            attempts -= 1
            time.sleep(delay)
        return [0]

    def get_image(self, prompt, style='DEFAULT', width=1024, height=1024):
        model_id = self.get_model()
        uuid = self.generate(prompt=prompt, style=style, width=width, height=height, model=model_id)
        image_raw = self.check_generation(uuid)[0]
        if image_raw:
            image_ready = Text2ImageAPI.decode_image(image_raw)
            image_path = Text2ImageAPI.dump_image(image_ready)
            return image_path
        else:
            return 0

    @staticmethod
    def decode_image(image):
        image_decoded = base64.b64decode(image)
        return image_decoded

    @staticmethod
    def dump_image(image_ready, img_dir='generated_images'):
        dir_lst = list(map(int, [x.replace('.jpg', '') for x in os.listdir(img_dir)]))
        max_name = max(dir_lst) if dir_lst else 0
        path = f'{img_dir}/{max_name + 1}.jpg'
        with open(path, 'wb') as file:
            file.write(image_ready)
        return path


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    SECRET_KEY = os.environ.get('SECRET_KEY')
    API_KEY = os.environ.get('API_KEY')
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', SECRET_KEY, API_KEY)
    prompt = 'Красивая девушка-программистка на python'
    print(api.get_image(prompt))

    # AUTH_HEADERS = {
    #     'X-Secret': f'Secret {SECRET_KEY}',
    #     'X-Key': f'Key {API_KEY}'
    # }
    # response = requests.get('https://api-key.fusionbrain.ai/key/api/v1/text2image/availability', headers=AUTH_HEADERS)
    # data = response.json()
    # print(data)
