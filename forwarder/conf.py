import os

from decouple import config

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SOURCE_DIR)

REDIS_ADDRESS = config('REDIS_ADDRESS', default='localhost')
REDIS_PORT = config('REDIS_PORT', default='6379')

SERVICE_STREAM_KEY = config('SERVICE_STREAM_KEY')
SERVICE_CMD_KEY = config('SERVICE_CMD_KEY')

LOGGING_LEVEL = config('LOGGING_LEVEL', default='DEBUG')