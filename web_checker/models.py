from web_checker import db
from datetime import datetime

class Urls(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    url = db.Column(db.String(1000),nullable=False)
    attempt = db.Column(db.Integer)
    status = db.Column(db.String(100),nullable=False)
    register_time = db.Column(db.DateTime,nullable=False)
    def __repr__(self):
        return f"Url: '{self.url}', '{self.attempt}', '{self.status}'"
