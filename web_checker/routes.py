from web_checker.models import Urls
from web_checker.functions import register_url, url_status,update_url_db,process_block_call
from web_checker import app, crontab, db
from flask import request, render_template
import subprocess
from sqlalchemy import desc
import web_checker
@app.route('/',methods =['POST'])
def entry():
    url = request.form['url']
    status, url = register_url(url)
    st = ''
    if status:
        return f'Registered {url} You shall be notified when its up!'
    else:
        return f'Bad Url: {url}'

@app.route('/checkUrls')
def list_all():
    strings = '\n'.join([str(url) for url in url_status()])
    return strings

@crontab.job()
def updatedb():
    update_url_db()
    return 'updated the database!'

@app.route('/block')
def block_click():
    process_block_call()
    return 'Opened chrome bitch'

