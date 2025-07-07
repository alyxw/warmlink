import yaml
import requests
import os
from PIL import Image

file_path = 'assets.yaml'
useragent = {"User-Agent": "python3 warmlink running for alyx.sh; https://github.com/alyxw/warmlink"}


def filter_88x31(tmpfile):
    try:
        if not os.path.exists(tmpfile):
            return False

        with Image.open(tmpfile) as img:
            width, height = img.size
            if width == 88 and height == 31:
                return True
            else:
                return False
    except Exception as e:
        return False


def processAsset(asset):
    print(f"working on {asset['source']}")
    os.makedirs(os.path.dirname(os.path.join('tmp', asset['dest'])), exist_ok=True)
    tmpfile = f'tmp/{asset['dest']}'
    try:
        response = requests.get(asset['source'], stream=True)
        response.raise_for_status()
        with open(tmpfile, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File downloaded successfully.")
        if (asset['validation'] == '88x31'):
            print('file requires 88x31 validation')
            if (filter_88x31(tmpfile)):
                print(f'valid 88x31')







            else:
                print('invalid 88x31 :(')
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")


with open(file_path, 'r') as file:
    data = yaml.safe_load(file)
print("YAML data loaded successfully")
for asset in data['assets']:
    processAsset(asset)

# except FileNotFoundError:
#     print(f"Error: The file '{file_path}' was not found.")
# except yaml.YAMLError as e:
#     print(f"Error parsing YAML file: {e}")
