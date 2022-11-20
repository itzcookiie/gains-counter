import boto3
import pathlib
import os


BUCKET = 'gains-counter'
REGION_NAME = 'fra1'
SPACES_ENDPOINT = f'https://{REGION_NAME}.digitaloceanspaces.com'
FILES_SPACE_URL = 'https://${BUCKET}.${REGION_NAME}.digitaloceanspaces.com'

_ROOT_DIR = pathlib.Path(__file__).parent
_ENV_FILE_NAMES = {
    'PROD': '.env',
    'DEV': '.env.dev'
}


session = boto3.session.Session()
client = session.client('s3',
                        region_name=REGION_NAME,
                        endpoint_url=SPACES_ENDPOINT,
                        aws_access_key_id=os.getenv('SPACES_KEY'),
                        aws_secret_access_key=os.getenv('SPACES_SECRET'))


def upload_file(filename, filepath):
    client.upload_file(filepath, BUCKET, filename, ExtraArgs={'ACL': 'public-read'})


def get_file_url(filename):
    return f'{FILES_SPACE_URL}/{filename}'


def download_file(filename: str):
    client.download_file(BUCKET,
                         filename,
                         str(_ROOT_DIR.joinpath(_ENV_FILE_NAMES[os.getenv('CHOSEN_ENV')])))