from web_checker.models import Urls
from web_checker.functions import register_url, url_status,update_url_db 
from web_checker import app, crontab, db
from flask import request

@app.route('/',methods =['POST'])
def entry():
    url = request.form['url']
    status, url = register_url(url)
    st = ''
    if status:
        return 'Registered {url}. You shall be notified when its up!'
    else:
        return 'Bad Url: {url}'


@app.route('/checkUrls')
def list_all():
    strings = '\n'.join([str(url) for url in url_status()])
    return strings


@app.route('/updatedb')
def updatedb():
    update_url_db()
    return 'updated the database!'
