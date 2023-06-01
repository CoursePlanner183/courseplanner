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
    return dict(
        courses=courses,
        add_course_url = URL('add_courses', signer=url_signer),
        delete_course_url = URL('delete_courses', signer=url_signer)
        )

@action('get_courses')
@action.uses(db, auth.user, url_signer)
def get_courses():
    courses = db(db.course).select().as_list()
    courses_taken = db(db.course_taken.user_id == auth.user_id).select().as_list()
    #print(courses_taken)
    #print(db(db.course_taken.user_id).select().as_list())
    #print(auth.user_id)
    return dict(
        id=auth.user_id,
        courses=courses,
        courses_taken=courses_taken,
        )

 
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
        redirect(URL("index"))
    return dict(form=form)


@action("add_courses", method="POST")
@action.uses(db, auth.user)
def add_courses():
    courses_selected = request.json.get('courses_selected')
    assert courses_selected is not None
    for courseId in courses_selected:
        if len(db(db.course_taken.course_id == courseId).select().as_list()) > 0:
            return "Course is already taken"

        db.course_taken.insert(
            course_id=courseId,
            is_enrolled=True,
            user_id = auth.user_id
        )
    return "ok"

@action("delete_courses", method="POST")
@action.uses(db, auth.user)
def delete_courses():
    courses_delete = request.json.get('courses_delete')
    for courseId in courses_delete:
        db((db.course_taken.course_id == courseId)).delete()
    return "ok"


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
