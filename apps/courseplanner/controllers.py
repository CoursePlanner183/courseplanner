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
    print(auth.user_id)
    return dict(
        courses=courses,
        add_course_url=URL('add_courses', signer=url_signer),
        delete_course_url=URL('delete_courses', signer=url_signer),
        edit_course_url=URL('edit_course', signer=url_signer),
        share_courses_url= URL('share_courses', signer=url_signer),
    )

@action('course/create', method=["GET", "POST"])
@action.uses('course.html', db, auth.user, url_signer)
def create_course():
    form = Form(db.course,deletable=False, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL("index"))
    return dict(form=form)

@action('get_courses')
@action.uses(db, auth.user, url_signer)
def get_courses():
    courses = db(db.course).select().as_list()
    courses_taken = db(db.course_taken.user_id == auth.user_id).select().as_list()
    return dict(
        id=auth.user_id,
        courses=courses,
        courses_taken=courses_taken,
        )

@action('get_planners', method="GET")
@action.uses(db, auth.user, url_signer)
def get_planners():
    user_id = request.params.get('user_id')
    courses = db(db.course).select().as_list()
    courses_taken = db(db.course_taken.user_id == user_id).select(orderby=db.course_taken.year).as_list()
    return dict(
        courses=courses,
        courses_taken=courses_taken
    )

@action('share')
@action.uses('share.html', db, auth.user, url_signer)
def share():
    return dict(
        get_planners_url= URL('get_planners', signer=url_signer),
    )
 
@action('user/profile', method=["GET","POST"])
@action.uses('user.html', db, auth.user, url_signer)
def profile():
    if request.method == "POST":
        student = { k: v for k, v in request.forms.items() if k in ['id', 'user_id', 'school_id', 'major', 'grad_start_date', 'grad_end_date']}
        db.student(student["id"]).update_record(
            school_id=student["school_id"],
            major=student["major"],
            grad_start_date=student["grad_start_date"],
            grad_end_date=student["grad_end_date"]
        )
        user = { k: v for k, v in request.forms.items() if k in ["email", "first_name", "last_name"]}
        db.auth_user(auth.user_id).update_record(
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
        )
        redirect(URL('user/profile'))
    return dict()


@action('edit_course', method=["GET", "POST"])
@action.uses('edit_course.html', db, session, auth.user, url_signer)
def edit_course():
    if request.method == 'GET':
        course_id = request.params.get('course_id')
        course = db.course(course_id)
        if course is None:
            redirect(URL('index'))

        form = Form(
            [
                Field("name", default=course.name, type='string'),
                Field("number", default=course.number, type="integer"),
                Field("credits", default=course.credits, type="integer"),
                Field("offering", default=course.offering, type='string', requires=IS_IN_SET(['Fall', 'Winter', 'Spring', 'Summer'])),
                Field("year", default=course.year, type="integer"),
            ],
            csrf_session=session,
            formstyle=FormStyleBulma,
        )

        return dict(form=form, course_id=course_id)

    # get POST request
    course_id = request.forms.get('course_id')
    course = db.course(course_id)
    if course is None:
        redirect(URL('index'))

    form = Form(
        [
            Field("name", default=request.forms.get('name'), type='string'),
            Field("number", default=request.forms.get('number'), type="integer"),
            Field("credits", default=request.forms.get('credits'), type="integer"),
            Field("offering", default=request.forms.get('offering'), type='string', requires=IS_IN_SET(['Fall', 'Winter', 'Spring', 'Summer'])),
            Field("year", default=request.forms.get('year'), type="integer"),
        ],
        csrf_session=session,
        formstyle=FormStyleBulma,
    )

    if form.accepted:
        course.update_record(
            name=form.vars['name'],
            number=form.vars['number'],
            credits=form.vars['credits'],
            offering=form.vars['offering'],
            year=form.vars['year']
        )
        redirect(URL('index'))

    return dict(form=form, course_id=course_id)


@action("add_courses", method="POST")
@action.uses(db, auth.user)
def add_courses():
    courses_selected = request.json.get('courses_selected')
    assert courses_selected is not None
    for courseId in courses_selected:
        if len(db(db.course_taken.course_id == courseId).select().as_list()) > 0:
            return "Course is already taken"
        data = db(db.course.id == courseId).select().as_list()
        print(data)
        print(courseId)
        db.course_taken.insert(
            course_id=courseId,
            is_enrolled=True,
            user_id = auth.user_id,
            year = data[0]['year'],
            season = data[0]['offering'],
        )
    return "ok"

@action("delete_courses", method="POST")
@action.uses(db, auth.user)
def delete_courses():
    courses_delete = request.json.get('courses_delete')
    for courseId in courses_delete:
        db((db.course_taken.course_id == courseId)).delete()
    return "ok"


@action('grades/calculator', method=["GET", "POST"])
@action.uses('calculator.html', db, auth.user, url_signer)
def calc():
    return dict()


@action('get_my_courses')
@action.uses(db, auth.user, url_signer)
def get_my_courses():
    query = (db.course_taken.user_id == auth.user_id) & (db.course_taken.course_id == db.course.id)
    courses_taken = db(query).select().as_list()
    courses_taken = [{**c["course"], **c["course_taken"]} for c in courses_taken]
    return dict(courses_taken=courses_taken)


@action('grade_categories')
@action.uses(db, auth.user, url_signer)
def get_grade_categories():
    course_taken_id = request.params.get('course_taken_id')
    query = (db.course_grade_categories.user_id == auth.user_id) & (db.course_grade_categories.course_taken_id == course_taken_id)
    grade_categories = db(query).select().as_list()
    
    query = db.course_taken.id == request.params.get('course_taken_id')
    grade = db(query).select().as_list()[0]["final_grade"]
    return dict(grade_categories=grade_categories, grade=grade)


@action('grade_categories', method='POST')
@action.uses(db, auth.user, url_signer)
def post_grade_categories():
    course_taken_id = request.json.get('course_taken_id')
    categories = request.json.get('grade_categories')
    query = (db.course_grade_categories.user_id == auth.user_id) & (db.course_grade_categories.course_taken_id == course_taken_id)
    db(query).delete()
    
    records = [{**gc, "user_id": auth.user_id, "course_taken_id": course_taken_id} for gc in categories]
    
    db.course_grade_categories.bulk_insert(records)
    
    return "ok"


@action('submit_grade', method="POST")
@action.uses(db, auth.user, url_signer)
def submit_grade():
    course_id = request.json.get('course_id')
    grade = request.json.get('grade')
    query = db.course_taken.id == course_id
    db(query).update(final_grade=grade)
    return dict(course_id=course_id, grade=grade)


@action('universities')
@action.uses(db, auth.user, url_signer)
def universities():
    schools = db(db.school).select().as_list()
    return dict(schools=schools)

@action('me')
@action.uses(db, auth.user, url_signer)
def me():
    query = (db.auth_user.id == auth.user_id) & (db.auth_user.id == db.student.user_id)
    x = db(query).select().as_list()[0]
    return { **x["auth_user"], **x["student"] }


@action('share_courses', method="POST")
@action.uses(db, auth.user, url_signer)
def share_courses():
    db(db.course_taken.user_id == auth.user_id).update(is_shared=True)
    return "ok"
