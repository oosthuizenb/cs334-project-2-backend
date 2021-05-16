import json
import csv

from .auth import token_required
from flask import Blueprint, request
from .database.models.enron import Employee, Recipient, Message
from .database.models import db
#from datetime import datetime
employees = Blueprint('employees', __name__)


@employees.route('/allemployees', methods=['GET'])
@token_required
def get_all_employees(current_user):
    employees = Employee.query.all()
    # messages = Message.query.all()
    # print(messages)
    # i = 0
    # for m in messages:
    #     # print(m)
    #     db.session.delete(m)
    #     if i % 20000 == 0:
    #         print('20000 messages')
    #         print(m)
    #         db.session.commit()
    #     i += 1
    # db.session.commit()
    # print(employees)
    all_employees: list = []
    for e in employees:
        all_employees.append({
            "eid": e.eid,
            "firstname": e.firstname,
            "lastname": e.lastname,
            "email_id": e.email_id
        })
    return json.dumps(all_employees), 200


@employees.route('/get_employee_info', methods=['POST'])
@token_required
def get_employee_info(current_user):
    print("the current user: ", current_user)
    eid = request.get_json()['data']['eid']
    #x = datetime(2001, 1, 1)
    #y = datetime(2001, 5, 27)
    employee = Employee.query.filter_by(eid=eid).all()[0]
    # number of emails sent in total

    messages = Message.query.all()
    mid_list: list = []
    for message in messages:
        #currdate = datetime.strptime(message.date, '%Y-%m-%d %H:%M:%S')
        if message.sender == employee.email_id:  # and currdate > x and currdate < y:
            mid_list.append(message.mid)

    list_of_employee_dict = []
    list_emp = []
    recipients = Recipient.query.all()
    emails_sent = 0
    print(len(mid_list))
    for r in recipients:
        if r.mid in mid_list:
            if r.rtype == 'TO':
                emails_sent += 1
                if len(list_of_employee_dict) == 0:
                    list_of_employee_dict.append({
                        "employee": r.rvalue,
                        "messages_sent": 1
                    })
                elif not any(a['employee'] == r.rvalue for a in list_of_employee_dict):
                    # does not exist
                    list_of_employee_dict.append({
                        'employee': r.rvalue,
                        'messages_sent': 1
                    })
                else:
                    # does exist
                    # both methods take equally long so there was not reason to get fancy : []
                    # method 1
                    # d = next(
                    #     item for item in list_of_employee_dict if item['employee'] == r.rvalue)
                    # d['messages_sent'] += 1
                    # methods 2
                    for x in list_of_employee_dict:
                        if x['employee'] == r.rvalue:
                            x['messages_sent'] += 1

    # now just need to extract the top 5
    # i dont understand this code hav

    for x in list_of_employee_dict:
        if x['employee'] == 'undisclosed-recipients@enron.com':
            list_of_employee_dict.remove(x)
    newList = sorted(list_of_employee_dict,
                     key=lambda k: k['messages_sent'], reverse=True)
    if len(newList) > 5:
        newnewlist = newList[:5]
    else:
        newnewlist = newList
    newnewlist.append({"totalMessages": emails_sent})

    return json.dumps(newnewlist), 200

    # query firstname
    # query lastname
    # add two together

    # query messages, see how many messages has sender field that's equal to employee email_id field.
    # make list of all employees this employee has sent emails to
    # retrieve top 5 employees based on amount of emails.


@employees.route('/fillrelationships', methods=['GET'])
def fill_recipient_relationships():
    recipients = Recipient.query.all()

    for recipient in recipients:
        employee = Employee.query.filter_by(email_id=recipient.rvalue).first()
        if employee:
            recipient.eid = employee.eid
            db.session.commit()
            print(recipient)

    print('fill relationships')
    return json.dumps({}), 200


@employees.route('/createdata', methods=['GET'])
@token_required
def create_data(current_user):
    print('create data')
    # with open('EmployeeList.csv') as f:
    #     reader = csv.reader(f)
    #     row_number = 0
    #     for row in reader:
    #         # print(row[0])
    #         if row_number != 0:
    #             e = Employee(row[0],row[1],row[2],row[3])
    #             # print('whatsupp')
    #             db.session.add(e)
    #         row_number += 1
    #         db.session.commit()

    print('dunzos with employees')
    with open('Message.csv') as f:
        reader = csv.reader(f)
        row_number = 0

        for row in reader:
            if row_number != 0:
                m = Message(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                )
                db.session.add(m)
                if row_number % 10000 == 0:
                    db.session.commit()
                    print(m)
            row_number += 1

    with open('RecipientInfo.csv') as f:
        reader = csv.reader(f)
        row_number = 0

        for row in reader:
            if row_number != 0:
                r = Recipient(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                )
                db.session.add(r)
                if row_number % 10000 == 0:
                    db.session.commit()
            row_number += 1
    return json.dumps({}), 200
