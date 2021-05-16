from . import db
from flaskapp import app


class Employee(db.Model):
    def __init__(self, eid, firstname, lastname, email_id):
        self.eid = eid
        self.firstname = firstname
        self.lastname = lastname
        self.email_id = email_id

    __tablename__ = 'employee_list'
    eid = db.Column(db.Integer, primary_key=True, nullable=True)
    firstname = db.Column(db.String(31))
    lastname = db.Column(db.String(31))
    email_id = db.Column(db.String(31))


class Message(db.Model):
    def __init__(self, mid, sender, date, message_id, subject, folder):
        self.mid = mid
        self.sender = sender
        self.date = date
        self.message_id = message_id
        self.subject = subject
        self.folder = folder

    __tablename__ = 'message'
    mid = db.Column(db.Integer, primary_key=True, nullable=True)
    sender = db.Column(db.String(127))
    date = db.Column(db.DateTime)
    message_id = db.Column(db.String(127))
    subject = db.Column(db.Text)
    folder = db.Column(db.String(127))


class Recipient(db.Model):
    def __init__(self, rid, mid, rtype, rvalue):
        self.rid = rid
        self.mid = mid
        self.rtype = rtype
        self.rvalue = rvalue

    __tablename__ = 'recipient_info'
    rid = db.Column(db.Integer, primary_key=True, nullable=True)
    mid = db.Column(db.Integer)
    rtype = db.Column(db.String(30))
    rvalue = db.Column(db.String(127))
    # eid = db.Column(db.Integer, db.ForeignKey('employee_list.eid'),
    #     nullable=True)
    # employee = db.relationship('Employee',
    #     backref=db.backref('recipients', lazy=True))
