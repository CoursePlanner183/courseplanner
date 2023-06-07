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
from py4web.utils.form import Form, FormStyleDefault, FormStyleBulma, SelectWidget,CheckboxWidget,RadioWidget
from .models import get_username, csu_schools, uc_schools
from pydal.validators import *

url_signer = URLSigner(session)


@action('index')
@action.uses('index.html', db, auth.user, url_signer)
def index():
    courses = db(db.course).select().as_list()
    print(auth.user_id)
    return dict(
        courses=courses,
        add_course_url=URL('course/add', signer=url_signer),
        delete_course_url=URL('delete_courses', signer=url_signer),
        edit_course_url=URL('course/edit', signer=url_signer),
        share_courses_url= URL('share_courses', signer=url_signer),
    )


@action('course/create', method=["GET", "POST"])
@action.uses('course.html', db, auth.user, url_signer)
def create_course():
    form = Form(db.course, deletable=False, formstyle=FormStyleBulma)
    form.structure.find('[name=offering]')[0]['_class'] = 'custom-select'
    if form.accepted:
        redirect(URL("index"))
    return dict(form=form)


@action('get_courses')
@action.uses(db, auth.user, url_signer)
def get_courses():
    courses = db(db.course).select().as_list()
    courses_taken = db(db.course_taken.user_id ==
                       auth.user_id).select().as_list()
    return dict(
        id=auth.user_id,
        courses=courses,
        courses_taken=courses_taken,
    )

@action('course/all', method=["GET"])
@action.uses('courses_list.html', db, auth.user, url_signer)
def course_list():
    user = auth.get_user()
    rows = db(db.course.created_by == user["id"]).select()
    for row in rows:
        print("rows is ", row["offering"])
        row["offering"] = ", ".join(row["offering"])
    return dict(rows=rows)
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

@action('course/history', method=["GET", "POST"])
@action.uses('course_history.html', db, auth.user, url_signer)
def course_history():
    user = auth.get_user()
    rows = db(db.course.created_by == user["id"]).select()
    for row in rows:
        print("rows is ", row["offering"])
        row["offering"] = ", ".join(row["offering"])
    return dict(rows=rows)


@action('user/profile',method=["GET", "POST"])
@action.uses('user.html', db, auth.user, url_signer, session)
def profile():

    Fields = []
    for field in db.auth_user:
        if(field.name == 'username'):
            print("name is ", field.name)
            print("writable is ", field.writable)
            print("readable is ", field.readable)
            field.writable = False
            field.readable = True
            print("requires is ", field.requires)
        Fields.append(field)
    Fields.append(Field('grad_date', type='date'))
    all_schools = [school[0] for school in csu_schools] + [school[0] for school in uc_schools]
    Fields.append(Field('School', type='string',
                  requires=IS_IN_SET(all_schools)))
    form = Form(Fields, deletable=False, formstyle=FormStyleBulma, csrf_session=session)

    print("FORM IS GAME", form.accepted)
    if form.accepted:
        print('GAMEEEEEE')
        db.auth_user.update((db.auth_user.id == auth_user["id"]),
                            username=form.vars['username'],
                            email=form.vars['email'],
                            first_name=form.vars['first_name'],
                            last_name=form.vars['last_name'])
        picked_school_id = db(db.school.name == form.vars['School']).select().first()["id"]
        db.student.update((db.student.user_id == auth_user["id"]),
                          grad_date=form.vars['grad_date'],
                          school_id=picked_school_id)
        redirect(URL('index'))
    # Adds user profile info if it exists
    auth_user = auth.get_user()

    if(auth_user is not None):
        form.vars['username'] = auth_user["username"]
        form.vars['email'] = auth_user["email"]
        form.vars['first_name'] = auth_user["first_name"]
        form.vars['last_name'] = auth_user["last_name"]
        user = db(db.student.user_id == auth_user["id"]).select().first()
        print(user)
        if user is not None:
            form.vars["grad_date"] = user["grad_date"]
            form.vars["school"] = db(
                db.school.id == user["school_id"]).select().first()["name"]

    return dict(form=form)


@action('course/edit', method=["GET", "POST"])
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


@action("course/search", method="GET")
@action.uses(db, auth.user)
def search_course():
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

@action("course/add", method="POST")
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


@action('share_courses', method="POST")
@action.uses(db, auth.user, url_signer)
def share_courses():
    db(db.course_taken.user_id == auth.user_id).update(is_shared=True)
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
            db.school.insert(name=school_name, abbr=abbr,
                             state=state, state_abbr=state_abbr)

    for school_name, abbr, state, state_abbr in uc_schools:
        school = db.school(name=school_name)
        if school:
            school.update_record(abbr=abbr, state=state, state_abbr=state_abbr)
        else:
            db.school.insert(name=school_name, abbr=abbr,
                             state=state, state_abbr=state_abbr)
