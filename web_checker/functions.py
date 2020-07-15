import requests
from requests.exceptions import RequestException, HTTPError,ConnectionError, Timeout
from requests.exceptions import InvalidURL,InvalidHeader, MissingSchema
from time import sleep
from web_checker.models import Urls
from web_checker import db
from datetime import datetime
import subprocess
import os
from sqlalchemy import desc

attempt_limit=3
update_log_file='/home/piojox/db_log_file'
block_file='/tmp/url_checker'
block_signal=13
block_msg='URL is up!'

web_status={'Down':'down',# No anduvo la ultima vez(Inicializamos asi)
            'Dead':'dead',# supero la cantidad maxima de llamados
            'Up':'up',#esta andando
        }


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
        except (InvalidURL,InvalidHeader,ConnectionError) as e:
            raise e
        except RequestException:
            return url


def register_url(url):
    """ Register to the URL to be processed later"""
    try:
        url = validate_Url(url)
    except (InvalidURL,InvalidHeader,ConnectionError) as e:
        return False, url
    db.session.add(Urls(url=url,attempt=0,status=web_status['Down'],register_time=datetime.now()))
    db.session.commit()
    return True, url



def update_url(url):
    print(f'updating {url.url}')
    link = url.url
    attempt = url.attempt
    if url.status == 'dead':
        print(f'its dead!')
        return
    elif url.status == 'up':
        print(f'its up! {url.url}')
        return
    attempt += 1
    curr_status = check_web(link)
    if curr_status:
        url.status = web_status['Up']
        print(f'its now up! {url.url}')
    elif attempt > attempt_limit:
        db.session.delete(url)
        print(f'too many calls... killing it {url.url}')
    else:
        url.status = web_status['Down']
        print(f'still down {url.url}')
    url.attempt = attempt

    
def update_url_db():
    urls = Urls.query.all()
    for url in urls:
        update_url(url)
    ups,downs,deads=url_status()
    print(len(ups))
    if len(ups) > 0:
        call_block()
    else:
        block_terminate()
    db.session.commit() 
    temp_update_log()

def url_status():
    deads=Urls.query.filter_by(status='dead').all()
    ups=Urls.query.filter_by(status='up').all()
    downs=Urls.query.filter_by(status='down').all()
    return ups,downs,deads

def send_notification(url):
    print(f'{url} is running!')

def temp_update_log():
    print('updating db')
    with open(update_log_file,'w') as f:
        f.write('updating db @'+str(datetime.now().time()))

def call_block():
    with open(block_file,'w') as f:
        f.write(block_msg)
    subprocess.Popen(['pkill',f'-RTMIN+{block_signal}','i3blocks'])

def block_terminate():
    os.remove(block_file)
    subprocess.Popen(['pkill',f'-RTMIN+{block_signal}','i3blocks'])
    return None

def process_block_call():
    url=Urls.query.order_by(desc(Urls.register_time)).first()
    subprocess.Popen(['chromium',url.url])
    db.session.delete(url)
    update_url_db()
    return None


