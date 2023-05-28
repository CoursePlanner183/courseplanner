"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

import datetime
import random

from py4web import action, request, abort, redirect, URL, Field
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from py4web.utils.form import Form, FormStyleDefault,FormStyleBulma,SelectWidget
from .models import get_username
from pydal.validators import *

url_signer = URLSigner(session)


@action('index')
@action.uses('index.html', db, auth.user, url_signer)
def index():
    courses = db(db.course).select().as_list()
    return dict(courses=courses)

@action('get_courses')
@action.uses(db, auth.user, url_signer)
def get_courses():
    courses = db(db.course).select().as_list()
    print(courses)
    return dict(courses=courses)

 
@action('user/profile')
@action.uses('user.html', db, auth.user, url_signer)
def profile():
    user = auth.get_user()
    Fields = []
    for field in db.auth_user:
        Fields.append(field)
    Fields.append(Field('grad_date', type='date'))
    Fields.append(Field('School', type='string',requires=IS_IN_SET(csu_schools + uc_schools)))
    form = Form(Fields,deletable=False, formstyle=FormStyleBulma)

    return dict(form=form)

@action('course/create', method=["GET", "POST"])
@action.uses('course.html', db, auth.user, url_signer)
def create_course():
    form = Form(db.course,deletable=False, formstyle=FormStyleBulma)
    if form.accepted:
        x = db.course.insert(name=form.vars["name"],number=form.vars["number"],credits=form.vars["credits"])
        redirect(URL("index"))
    return dict(form=form)


@action("course/add", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def add_courses():
    courses = request.json.get('courses_selected')
    user = auth.get_user()
    assert user is not None and courses is not None
    for courseId in courses:
        db.course_taken.insert(
            user_id=user['id'],
            course_id=courseId,
            is_enrolled=True,
        )
    return "ok"

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
            db.school.insert(name=school_name, abbr=abbr, state=state, state_abbr=state_abbr)

    for school_name, abbr, state, state_abbr in uc_schools:
        school = db.school(name=school_name)
        if school:
            school.update_record(abbr=abbr, state=state, state_abbr=state_abbr)
        else:
            db.school.insert(name=school_name, abbr=abbr, state=state, state_abbr=state_abbr)
