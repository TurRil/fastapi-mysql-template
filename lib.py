import os

def check_cfg():
    return os.path.isfile('.env')

def get_cfg():
    from app.settings import Settings # in python 3.15 use lazy load

    settings = Settings()
    return settings
