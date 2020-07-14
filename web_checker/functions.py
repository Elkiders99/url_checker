import requests
from requests.exceptions import RequestException, HTTPError,ConnectionError, Timeout
from requests.exceptions import InvalidURL,InvalidHeader, MissingSchema
from time import sleep
from web_checker.models import Urls
from web_checker import db


web_status={'Down':'down',# No sabemos si esta up o no(Inicializamos asi)
            'Dead':'dead',# supero la cantidad maxima de llamados
            'Up':'up',#esta andando
        }

class TooManyCallsError(Exception):
    def __init__(self,url,attempt):
        self.url = url
        self.attempt = attempt


def check_web(web,timeout=None):
    """Chequea si una url esta andando 
    Devuelve True cuando logro que ande, si llega al limite devuelve tira TooManyCallsError"""
    try:
         if timeout:
             requests.get(web).raise_for_status()
             return True
         else:
            requests.get(web).raise_for_status()
            return True
    except RequestException as e:
        return False
 

def add_schema(web):
    web = 'http://'+web
    return web


def validate_Url(url):
    """ Chequea si una url es correcta e intenta corregirla
    devuelve la url si pasa el chequeo, tira InvalidURL o Invalid Header si no"""
    while True:
        try:
            response = requests.get(url)
            if response.ok:
                return url
        except MissingSchema as e:
            url = add_schema(url)
        except (InvalidURL,InvalidHeader) as e:
            raise e
        except RequestException:
            return url


def register_url(url):
    """ Register to the URL to be processed later"""
    try:
        url = validate_Url(url)
    except (InvalidURL,InvalidHeader) as e:
        return False, url
    db.session.add(Urls(url=url,attempt=0,status=web_status['Down']))
    db.session.commit()
    return True, url


def succesful_check(url):
    db.session.delete(url)
    db.session.commit()
    send_notification(url.url)


def update_url(url):
    print(f'updating {url.url}')
    link = url.url
    attempt = url.attempt
    if url.status == 'dead':
        print('its dead!')
        return
    elif url.status == 'up':
        print('its up!')
        return
    attempt += 1
    curr_status = check_web(link)
    if curr_status:
        url.status = web_status['Up']
        print('its now up!')
    elif attempt > 5:
        url.status = web_status['Dead']
        print('too many calls... killing it')
    else:
        url.status = web_status['Down']
        print('still down')
    url.attempt = attempt

    
def update_url_db():
    urls = Urls.query.all()
    for url in urls:
        update_url(url)
    db.session.commit()



def url_status():
    deads=Urls.query.filter_by(status='dead').all()
    ups=Urls.query.filter_by(status='up').all()
    downs=Urls.query.filter_by(status='down').all()
    return ups,downs,deads

def send_notification(url):
    print(f'{url} is running!')

