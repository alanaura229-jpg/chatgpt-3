import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-btu-uaslp-2024')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///btu.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False