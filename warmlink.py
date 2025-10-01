import yaml
import requests
import os
from PIL import Image
import hashlib
import subprocess
import shutil

project_path = '/home/hugo-build/blogbuild/alyxsh/'

try:
    shutil.rmtree(project_path)
    os.mkdir(project_path)
except:
    print("nothing to remove")
    os.mkdir(project_path)
subprocess.run(['git', 'clone', 'git@git.en0.io:alyx/alyxsh.git', '.'], cwd=project_path)
subprocess.run(['git', 'config', 'user.name', 'alyxbot'], cwd=project_path)
subprocess.run(['git', 'config', 'user.email', 'hello@alyx.sh'], cwd=project_path)
subprocess.run(['hugo', '--cleanDestinationDir'], cwd=project_path)

file_path = f'{project_path}/warmlink-assets.yaml'
useragent = {"User-Agent": "python3 warmlink; https://github.com/alyxw/warmlink"}


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
                print(f'valid 88x31, running checksums')
                with open(tmpfile, "rb") as f:
                    tmphash = hashlib.file_digest(f, "sha512").hexdigest()
                with open(os.path.join(project_path, asset['dest']), "rb") as f:
                    prodhash = hashlib.file_digest(f, "sha512").hexdigest()

                if (tmphash != prodhash):
                    print("sum mismatch, replacing with updated asset")
                    os.replace(tmpfile, os.path.join(project_path, asset['dest']))
                    subprocess.run(['hugo'], cwd=project_path)
                    subprocess.run(['git', 'add', 'static/', 'public/'], cwd=project_path)
                    subprocess.run(['git', 'commit', '-m', f'Update {asset["dest"]}'], cwd=project_path)
                else:
                    print("no update needed")
            else:
                print('invalid 88x31 :(')
            os.remove(tmpfile)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")


with open(file_path, 'r') as file:
    data = yaml.safe_load(file)
print("YAML data loaded successfully")
for asset in data['assets']:
    processAsset(asset)

subprocess.run(['hugo'], cwd=project_path)
subprocess.run(['git', 'add', 'public/'], cwd=project_path)
subprocess.run(['git', 'commit', '-m', f'Build output changed'], cwd=project_path)
subprocess.run(['git', 'push', 'origin', f'main'], cwd=project_path)
# except FileNotFoundError:
#     print(f"Error: The file '{file_path}' was not found.")
# except yaml.YAMLError as e:
#     print(f"Error parsing YAML file: {e}")
