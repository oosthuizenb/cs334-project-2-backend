import pandas as pd
from sqlalchemy.sql.sqltypes import DATETIME, INTEGER, TEXT, Enum
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.types import Integer, TIMESTAMP, FLOAT, VARCHAR

user = "test"
password = "password"
host = "0.0.0.0"
database = "database"
port = "5432"

DATABASE_CONNECTION_URI = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'

engine = create_engine(DATABASE_CONNECTION_URI)

######
# adds csv files to postgres server RUN THIS FUNCTION ONLY ONCE


def csv_to_sql():
    emp = pd.read_csv('EmployeeList.csv')
    emp_name = 'employee_list'
    emp.to_sql(
        emp_name,
        engine,
        if_exists='replace',
        index=False,
        dtype={
            "eid": Integer,
            "firstname": VARCHAR(31),
            "lastname": VARCHAR(31),
            "email_id": VARCHAR(31),
        }

    )
    rec = pd.read_csv('RecipientInfo.csv')
    rec_name = 'recipient_info'
    rec.to_sql(
        rec_name,
        engine,
        if_exists='replace',
        index=False,
        dtype={
            "rid": Integer,
            "mid": INTEGER,
            "rtype": Enum("TO", "CC", "BCC", name='type'),
            "rvalue": VARCHAR(127),
        }

    )
    msg = pd.read_csv('Message.csv')
    msg_name = 'message'
    msg.to_sql(
        msg_name,
        engine,
        if_exists='replace',
        index=False,
        dtype={
            "mid": Integer,
            "sender": VARCHAR(127),
            "data": DATETIME,
            "message_id": VARCHAR(127),
            "subject": TEXT,
            "folder": VARCHAR(127),
        }

    )

    with engine.connect() as con:
        con.execute('ALTER TABLE employee_list ADD PRIMARY KEY (eid);')
        con.execute('ALTER TABLE message ADD PRIMARY KEY (mid);')
        con.execute('ALTER TABLE recipient_info ADD PRIMARY KEY (rid);')
        con.execute(
            'ALTER TABLE recipient_info ADD CONSTRAINT midfk FOREIGN KEY (mid) REFERENCES message (mid) MATCH FULL;')
        con.close()
######

# Gets name in the format of 'Name' or 'Lastname' or 'Name Lastname' (case insensitive)


def full_to_sender(fullname):
    fullname = fullname.lower()
    i = fullname.find(" ")
    if i == -1:
        fname = fullname
        sname = fullname
    else:
        fname = fullname[:i]
        sname = fullname[i+1:]
    con = engine.raw_connection()
    cur = con.cursor()
    cur.execute("SELECT employee_list.email_id FROM employee_list WHERE lower(firstname) = \'" +
                fname + "\' OR lower(lastname) = \'" + sname + "\';")
    row = cur.fetchone()
    con.close()
    if row is None:
        return ['no.address@enron.com']
    return row

# returns a list of all recipients of all emails from the specific sender


def find_recipients(email):
    undis = 'undisclosed-recepients@enron.com'
    all_contact = []
    con = engine.raw_connection()
    cur = con.cursor()
    cur.execute("SELECT recipient_info.rvalue FROM recipient_info INNER JOIN message ON recipient_info.mid=message.mid WHERE message.sender = \'" + email + "\';")
    all_contact = cur.fetchall()
    all_contact = [i[0] for i in all_contact]
    all_contact = list(filter(lambda a: a != undis, all_contact))
    cur.close()
    con.close()
    return all_contact


def most_common(lst):
    return max(set(lst), key=lst.count)

# returns top 5 most contacted people or top x most contacted people if less than 5 cotacted


def most_contacted(email):
    all_contact = find_recipients(email)
    most_contact = []
    loop = 5
    if len(set(all_contact)) <= 5:
        loop = len(set(all_contact))
    for i in range(loop):
        highest = most_common(all_contact)
        most_contact.append(highest)
        # removes most occuring
        all_contact = list(filter(lambda a: a != highest, all_contact))

    return most_contact

# returns number of emails sent between dates


def num_mail(email, startdate, enddate):
    between = []
    con = engine.raw_connection()
    cur = con.cursor()
    cur.execute("SELECT message.mid FROM message WHERE sender = \'" + email +
                "\' AND date BETWEEN \'" + str(startdate) + "\' AND \'" + str(enddate)+"\';")
    row = cur.fetchall()
    cur.close()
    con.close()
    return len(row)


def drop_tables():
    with engine.connect() as con:
        con.execute('DROP TABLE employee_list;')
        con.execute('DROP TABLE recipient_info;')
        con.execute('DROP TABLE message;')
        con.close()


def what_to_do():
    csv_to_sql()  # adds table to database, run it only once  (maybe make it it's own file if necessary). If you make its own file, remember
    # to change directories of the 3 pd.to_sql statements
    # get name from html form (Only name,/Only surname/Name Surname)
    name = "allen"
    # get dates (maybe use datepickers)
    startdate, enddate = "2001/01/01", "2001/05/27"
    email = full_to_sender(name)[0]  # converts given name to an email
    print(email)
    most = most_contacted(email)  # top 5 most contacted (or top x if x<5)
    # number of mails SENT between dates given
    i = num_mail(email, startdate, enddate)
    print(most)
    print(i)
    # drop_tables() #-> not sure if necessary, since database is always the same, it only ever has to be loaded once, so no point in dropping??


what_to_do()
