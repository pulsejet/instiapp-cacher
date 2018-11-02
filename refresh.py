import json
import requests
import shutil
import os
import errno
from PIL import Image

ROOT = '/var/www/instiapp/'
EVENTS = 'https://insti.app/api/events'
IMG_PREFIX = 'https://api.insti.app/static/upload/'
REPL_PREFIX = 'http://10.105.177.17/images/'

r = requests.get(EVENTS)
response = r.json()

def get_path(url):
    return url.replace(IMG_PREFIX, '')

def download_image(url):
    # Get the target file path    
    filename = ROOT + 'images/' + get_path(url)

    # Make directories recursively
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    # Check if the file already exists
    if not os.path.isfile(filename):
        print('Downloading', url)
        img = requests.get(url, stream=True)
        if img.status_code == 200:
            with open(filename, 'wb') as f:
                img.raw.decode_content = True
                shutil.copyfileobj(img.raw, f)

            # Convert progressive to standard JPEG
            image = Image.open(filename).convert('RGB')
            image.save(filename, 'JPEG', quality=100, optimize=False, progressive=False)

    return url.replace(IMG_PREFIX, REPL_PREFIX)

# Get images
for event in response['data']:
    event['image_url'] = download_image(event['image_url'])

    for body in event['bodies']:
        body['image_url'] = download_image(body['image_url'])

# Dump JSON
with open(ROOT + 'events.json', 'w') as fp:
    json.dump(response, fp)
