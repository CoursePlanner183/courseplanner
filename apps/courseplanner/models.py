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
    Field("name", type='string'),
    Field("number", type="integer"),
    Field("credits", type="integer"),
    Field("offering",type='string',requires=IS_IN_SET(['Fall','Winter','Spring','Summer'])),
    Field("year","integer"),
)

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
    Field("is_enrolled", type="boolean"),
    Field("season", requires=IS_IN_SET(['Fall', 'Winter', 'Spring', 'Summer'])),
    Field("year", type="integer"),
    Field("final_grade", tyoe="string"),
)

db.define_table(
    "course_grade_categories",
    Field("user_id", 'reference auth_user'),
    Field("course_taken_id", "reference course_taken", writable=False, readable=True),
    Field("category_name", type="string"),
    Field("grade", type="float"),
    Field("weight", type="float"),
)

db.student.id.writable = False
db.course.id.writable = False
db.commit()
