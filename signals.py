__author__ = 'shuaili'
from django.dispatch import Signal

# Signal used when model is saved
login_in_news = Signal(providing_args = ['instance', 'login_time'])
upload_news = Signal(providing_args = ['instance'])