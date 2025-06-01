from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Reload .env
load_dotenv()
os.environ.clear()


print("Current working directory:", os.getcwd())
print("initial MONGODB_URI:", os.getenv("MONGODB_URI"))
print("initial PAYHERO_CALLBACK_URL:", os.getenv("PAYHERO_CALLBACK_URL"))

current_dir = os.getcwd()
files_in_current_dir = os.listdir(current_dir)

print("Files in the current directory:")
for file in files_in_current_dir:
    print(file)


class Config(BaseSettings):
    MONGODB_URI: str
    DATABASE_NAME: str
    PAYHERO_STKPUSH_URL: str
    PAYHERO_USERNAME: str
    PAYHERO_PASSWORD: str
    PAYHERO_CALLBACK_URL: str
    LOG_LEVEL: str
    FRONTEND_URL: str
    PORT: int = 8000  # Default to 8000 if not set in .env

    class Config:
        env_file = ".env"

# Initialize configuration
config = Config()

# Expose variables
MONGODB_URI = config.MONGODB_URI
DATABASE_NAME = config.DATABASE_NAME
PAYHERO_STKPUSH_URL = config.PAYHERO_STKPUSH_URL
PAYHERO_USERNAME = config.PAYHERO_USERNAME
PAYHERO_PASSWORD = config.PAYHERO_PASSWORD
PAYHERO_CALLBACK_URL = config.PAYHERO_CALLBACK_URL
LOG_LEVEL = config.LOG_LEVEL
FRONTEND_URL = config.FRONTEND_URL
PORT = config.PORT

# Debugging (Optional: Remove in Production)
print(f"MONGODB_URI: {MONGODB_URI}")
print(f"DATABASE_NAME: {DATABASE_NAME}")
print(f"PAYHERO_STKPUSH_URL: {PAYHERO_STKPUSH_URL}")
print(f"PAYHERO_USERNAME: {PAYHERO_USERNAME}")
print(f"PAYHERO_PASSWORD: {PAYHERO_PASSWORD}")
print(f"PAYHERO_CALLBACK_URL: {PAYHERO_CALLBACK_URL}")
print(f"LOG_LEVEL: {LOG_LEVEL}")
print(f"PORT: {PORT}")
print(f"FRONTEND_URL: {FRONTEND_URL}")
