"""
This file defines the database models
"""

import datetime
import random
from py4web.utils.populate import FIRST_NAMES, LAST_NAMES, IUP
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_username():
    return auth.current_user.get('username') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


#Adding in some CSU and UC schools mostly for testing.
#TODO: Add more schools as needed and possible option for creating own schools
csu_schools = [
    ('California State University, Bakersfield', 'CSUB', 'California', 'CA'),
    ('California State University, Channel Islands', 'CSUCI', 'California', 'CA'),
    ('California State University, Chico', 'CSUC', 'California', 'CA'),
    ('California State University, Dominguez Hills', 'CSUDH', 'California', 'CA'),
    ('California State University, East Bay', 'CSUEB', 'California', 'CA'),
    ('California State University, Fresno', 'CSUF', 'California', 'CA'),
    ('California State University, Fullerton', 'CSUF', 'California', 'CA'),
    ('California State University, Long Beach', 'CSULB', 'California', 'CA'),
    ('California State University, Los Angeles', 'CSULA', 'California', 'CA'),
    ('California State University, Maritime Academy', 'CSUMA', 'California', 'CA'),
    ('California State University, Monterey Bay', 'CSUMB', 'California', 'CA'),
    ('California State University, Northridge', 'CSUN', 'California', 'CA'),
    ('California State University, Sacramento', 'CSUS', 'California', 'CA'),
    ('California State University, San Bernardino', 'CSUSB', 'California', 'CA'),
    ('California State University, San Marcos', 'CSUSM', 'California', 'CA'),
    ('California State University, Stanislaus', 'CSUS', 'California', 'CA'),
    # Add more CSU schools as needed
]
uc_schools = [
        ('University of California, Berkeley', 'UCB', 'California', 'CA'),
        ('University of California, Davis', 'UCD', 'California', 'CA'),
        ('University of California, Irvine', 'UCI', 'California', 'CA'),
        ('University of California, Los Angeles', 'UCLA', 'California', 'CA'),
        ('University of California, Merced', 'UCM', 'California', 'CA'),
        ('University of California, Riverside', 'UCR', 'California', 'CA'),
        ('University of California, San Diego', 'UCSD', 'California', 'CA'),
        ('University of California, San Francisco', 'UCSF', 'California', 'CA'),
        ('University of California, Santa Barbara', 'UCSB', 'California', 'CA'),
        ('University of California, Santa Cruz', 'UCSC', 'California', 'CA'),
        # Add more UC schools as needed
]


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later


db.define_table(
    "school",
    Field("name", type='string'),
    Field("abbr", type="string"),
    Field("state", type="string"),
    Field("state_abbr", type="string"),
)

db.define_table(
    "course",
    Field("abbrevation", type='string'),
    Field("number", type="integer"),
    Field("description", type="text"),
    Field("credits", type="integer"),
    Field("offering",type='list:string',requires=IS_IN_SET(['Fall','Winter','Spring','Summer'], multiple=True),multiple=True),
    Field("year","integer"),
    Field('created_by', 'reference auth_user', default=lambda: auth.user_id)
)

db.course.created_by.readable = db.course.created_by.writable = False
db.define_table(
    "student",
    Field("user_id", 'reference auth_user',writable=False,readable=True),
    Field("school_id","integer", "reference school"),
    Field("grad_date", type="date"),
)

db.define_table(
    "course_taken",
    Field("user_id", 'reference auth_user',writable=False,readable=True),
    Field("course_id", "reference course",writable=False,readable=True),
    Field("grade", "integer", "reference course",writable=False,readable=True),
    Field("status", type="string", requires=IS_IN_SET(['Enrolled','Taken','Withdrawn', 'Dropped'])),
    Field("season", requires=IS_IN_SET(['Fall', 'Winter', 'Spring', 'Summer'])),
    Field("year", type="integer"),
    Field("final_grade", tyoe="string"),
)

db.define_table(
    "course_grade_categories",
    Field("user_id", 'reference auth_user'),
    Field("course_id", "reference course", writable=False, readable=True),
    Field("category_name", type="string"),
    Field("grade", type="float"),
    Field("weight", type="float"),
)

db.student.id.writable = False
db.course.id.writable = False
db.commit()




