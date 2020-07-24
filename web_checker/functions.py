import requests
from requests.exceptions import RequestException, HTTPError,ConnectionError, Timeout,InvalidURL,InvalidHeader, MissingSchema
from web_checker.models import Urls
from web_checker import db,config
from datetime import datetime
import subprocess
import os
from sqlalchemy import desc
from urllib.parse import urlparse
import urllib3


attempt_limit = config['attempt_limit']
block_file = config['block_file']
block_signal = config['block_signal']
block_msg = config['block_msg']

web_status={'Down':'down',# No anduvo la ultima vez(Inicializamos asi)
            'Up':'up',#esta andando
        }


def check_web(url,timeout=None):
    """Chequea si una url esta andando
    Devuelve True cuando logro que ande"""
    try:
        http = urllib3.PoolManager()
        r = http.request('HEAD',url)
        return int(r.status) < 400
    except:
        return False

def validate_Url(url):
    """ Chequea si una url es correcta e intenta corregirla
    devuelve la url si pasa el chequeo, tira InvalidURL o Invalid Header si no"""
    parsed = urlparse(url)
    return parsed.scheme and parsed.netloc

def register_url(url):
    """ Register to the URL to be processed later"""
    validation = validate_Url(url)
    if validation:
        db.session.add(Urls(url=url,attempt=0,status=web_status['Down'],register_time=datetime.now()))
        db.session.commit()
        return True, url
    else:
        return False, url

def update_url(url):
    link = url.url
    attempt = url.attempt
    if url.status == 'dead':
        return
    elif url.status == 'up':
        return
    attempt += 1
    curr_status = check_web(link)
    if curr_status:
        url.status = web_status['Up']
    elif int(attempt) > attempt_limit:
        db.session.delete(url)
    else:
        url.status = web_status['Down']
    url.attempt = attempt

def update_url_db():
    urls = Urls.query.all()
    for url in urls:
        update_url(url)
    ups,downs,deads=url_status()
    if len(ups) > 0:
        call_block()
    else:
        block_terminate()
    db.session.commit()

def url_status():
    deads=Urls.query.filter_by(status='dead').all()
    ups=Urls.query.filter_by(status='up').all()
    downs=Urls.query.filter_by(status='down').all()
    return ups,downs,deads

def send_notification(url):
    print(f'{url} is running!')

def call_block():
    with open(block_file,'w') as f:
        f.write(block_msg)
    subprocess.Popen(['pkill',f'-RTMIN+{block_signal}','i3blocks'])

def block_terminate():
    try:
        os.remove(block_file)
        subprocess.Popen(['pkill',f'-RTMIN+{block_signal}','i3blocks'])
    except:
        pass

def process_block_call():
    url=Urls.query.order_by(desc(Urls.register_time)).first()
    if url:
        subprocess.Popen(['chromium',url.url])
        db.session.delete(url)
        update_url_db()
