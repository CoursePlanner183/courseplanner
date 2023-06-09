"""
This file defines the database models
"""

import datetime
import random
import string
from py4web.utils.populate import FIRST_NAMES, LAST_NAMES, IUP
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_username():
    return auth.current_user.get('username') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later


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


def add_california_schools():
    for school_name, abbr, state, state_abbr in csu_schools:
        school = db.school(name=school_name)
        if school:
            school.update_record(abbr=abbr, state=state, state_abbr=state_abbr)
        else:
            db.school.insert(name=school_name, abbr=abbr,
                             state=state, state_abbr=state_abbr)

    for school_name, abbr, state, state_abbr in uc_schools:
        school = db.school(name=school_name)
        if school:
            school.update_record(abbr=abbr, state=state, state_abbr=state_abbr)
        else:
            db.school.insert(name=school_name, abbr=abbr,
                             state=state, state_abbr=state_abbr)

db.define_table(
    "school",
    Field("name", type='string'),
    Field("abbr", type="string"),
    Field("state", type="string"),
    Field("state_abbr", type="string"),
)

db.define_table(
    "course",
    Field("name", type='string'),
    Field("abbreviation", type='string'),
    Field("number", type="integer"),
    Field("description", type="text"),
    Field("credits", type="integer"),
    Field("instructor", type="string"),
    Field("offering",type='list:string',requires=IS_IN_SET(['Fall','Winter','Spring','Summer'], multiple=True),multiple=True),
    Field("year","integer"),
    Field('created_by', 'reference auth_user', default=lambda: auth.user_id)
)

db.course.created_by.readable = db.course.created_by.writable = False
db.course.id.readable = db.course.id.writable = False

db.define_table(
    "student",
    Field("user_id", 'reference auth_user',writable=False,readable=True),
    Field("school_id", "reference school"),
    Field("grad_start_date", type="date"),
    Field("grad_end_date", type="date"),
    Field("major", type="string"),
)

db.define_table(
    "course_taken",
    Field("user_id", 'reference auth_user',writable=False,readable=True, default=lambda: auth.user_id),
    Field("course_id", "reference course",writable=False,readable=True),
    Field("grade", "integer", "reference course",default=100,writable=False,readable=True),
    Field("status", type="string", requires=IS_IN_SET(['Enrolled','Taken','Withdrawn', 'Dropped'])),
    Field("season", requires=IS_IN_SET(['Fall', 'Winter', 'Spring', 'Summer'])),
    Field("year", type="integer"),
    Field("final_grade", type="string"),
    Field("is_shared", type="boolean", default=False),
)


db.define_table(
    "course_grade_categories",
    Field("user_id", 'reference auth_user', default=lambda: auth.user_id),
    Field("course_taken_id", "reference course_taken", writable=False, readable=True),
    Field("category_name", type="string"),
    Field("grade", type="float"),
    Field("weight", type="float"),
)

# temp table, can be added to student once forced profiles can be worked out.
db.define_table(
    "shared_planner",
    Field("user_id", 'reference auth_user'),
    Field("name", type="string")
)

db.student.id.writable = False

db.commit()


def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def generate_random_course():
    course_types = ['ART', 'BIO', 'CHEM', 'CSE', 'ENG', 'HIST', 'MATH', 'PHYS', 'PSYC']
    professors = ["John Doe", "Jane Smith", "David Johnson", "Emily Davis", "Michael Brown"]
    name = generate_random_string(8) + " Course"
    abbreviation = random.choice(course_types)
    professor = random.choice(professors)
    description = generate_random_string(20) + " Lorem ipsum dolor sit amet."
    credits = random.randint(1, 5)
    number = random.randint(1, 500)
    offering = random.sample(['Fall', 'Winter', 'Spring', 'Summer'], random.randint(1, 4))
    year = 2023
    
    return {
        'name': name,
        'abbreviation': abbreviation,
        'number': number,
        'description': description,
        'instructor': professor,
        'credits': credits,
        'offering': offering,
        'year': year
    }

def insert_random_courses(num_courses):
    for _ in range(num_courses):
        course_data = generate_random_course()
        print("Inserting course",course_data )
        db.course.insert(**course_data)


db.commit()
