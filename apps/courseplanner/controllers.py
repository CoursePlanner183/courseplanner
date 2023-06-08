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
from .models import insert_random_courses, get_username
from pydal.validators import *

url_signer = URLSigner(session)


@action('index')
@action.uses('index.html', db, auth.user, url_signer)
def index():
    courses = db(db.course).select().as_list()
    curr_user = db.auth_user(auth.user_id)
    #db(db.course).delete()
    #db(db.course_taken).delete()
    #insert_random_courses(20)
    print(auth.user_id)
    return dict(
        courses=courses,
        curr_user=curr_user,
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
    form.structure.find('[class=select]')[0]["_class"] = "select is-multiple"
    if form.accepted:
        redirect(URL("index"))
    return dict(form=form)

@action('course/edit/<courseId:int>', method=["GET", "POST"])
@action.uses('course.html', db, session, auth.user, url_signer)
def edit_course(courseId=None):
    assert courseId is not None
    course = db.course[courseId]
    if(course.created_by != auth.user_id):
        redirect(URL('index'))
    if course is None:
        redirect(URL('index'))
    form = Form(db.course,record=course,deletable=False,formstyle=FormStyleBulma,csrf_session=session)
    form.structure.find('[name=offering]')[0]['_class'] = 'custom-select'
    form.structure.find('[class=select]')[0]["_class"] = "select is-multiple"
    if form.accepted:
        redirect(URL("index"))
    return (dict(form=form))

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
    print(db.student)
    return dict(
        courses=courses,
        courses_taken=courses_taken
    )

@action('share')
@action.uses('share.html', db, auth.user, url_signer)
def share():
    return dict(
        get_planners_url= URL('get_planners', signer=url_signer),
        get_shared_users_url= URL('get_shared_users', signer=url_signer),
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

@action("course/search", method=["GET","POST"])
@action.uses('search_course.html',db,session, auth.user)
def search_course():
    results = []
    searchForm = Form(
        [
            Field("course_name", default=request.forms.get('course_name'), type='string'),
            Field("course_number", default=request.forms.get('course_number'), type="integer"),
            Field("credits", default=request.forms.get('credits'), type="integer"),
            Field("offering",default=request.forms.get('offering'),type='list:string',requires=IS_IN_SET(['Fall','Winter','Spring','Summer'], multiple=True),multiple=True),
            Field("year", default=request.forms.get('year'), type="integer"),
        ],
        csrf_session=session,
        formstyle=FormStyleBulma,
    )

    #Edit form variables
    searchForm.structure.find('[name=offering]')[0]['_class'] = 'custom-select'
    searchForm.structure.find('[name=year]')[0]['_type'] = 'number'
    searchForm.custom.submit['_@click'] = 'Search()'  # Add custom inline CSS styles to the button
    #print(searchForm.structure)
   # searchForm.structure.find('form')[0]['_v-on:submit.prevent']= 'search'
    searchForm.structure.find('form')[0]['_id']= 'searchFormId'
    searchForm.structure.find('[class=select]')[0]["_class"] = "select is-multiple"
    #print("\n\n", searchForm.structure.find('form')[0], "\n\n")
    
    #print("searchForm.custom.submit is", searchForm.custom.submit)
    ShowSearch = True
    if searchForm.accepted:
        query = None
        print("vars are", searchForm.vars)
        if searchForm.vars['course_name'] != None or searchForm.vars["course_name"] != '':
            query = db.course.name == searchForm.vars['course_name']
        if searchForm.vars['course_number'] != None and searchForm.vars['course_number'] != '':
            query = query | (db.course.number == searchForm.vars['course_number'])
        if searchForm.vars['credits'] != None and searchForm.vars['credits'] != '':
            query = query | (db.course.credits == searchForm.vars['credits'])
        if searchForm.vars['offering'] != None and searchForm.vars['offering'] != '':
            query = query | (db.course.offering == searchForm.vars['offering'])
        if searchForm.vars['year'] != None and searchForm.vars['year'] != '':
            query = query | (db.course.year == searchForm.vars['year'])
        if(query != None):
            #query = query | db.course.created_by == auth.user_id
            results = db(query).select()
        for result in results:
            #Check to see if user is owner of course, if so allow course editing
            result["is_owner"] = result["created_by"] == auth.user_id
            #Check to see if user is enrolled in course, if so prevent deletion and also prevent adding to planner
            is_not_enrolled = len(db((db.course_taken.course_id == result["id"]) & (db.course_taken.user_id == auth.user_id)).select().as_list()) == 0
            result["is_not_enrolled"] = is_not_enrolled
        print("query is ",query)
        print("results are ",results)
        ShowSearch = False
    return dict(searchForm=searchForm,results=results,ShowSearch=ShowSearch)

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

@action("course/add/<courseId:int>")
@action.uses(db, session,auth.user)
def add_course(courseId=None):
    assert courseId is not None
    if len(db(db.course_taken.course_id == courseId).select().as_list()) > 0:
        return "Course is already taken"
    data = db(db.course.id == courseId).select().as_list()
    db.course_taken.insert(
        course_id=courseId,
        is_enrolled=True,
        user_id = auth.user_id,
        year = data[0]['year'],
        season = data[0]['offering'],
    )
    print("ADDED COURSE")
    #redirect(URL("course/search"))
    return "ok"

@action("course/delete/<courseId:int>",method="DELETE")
@action.uses(db, session,auth.user)
def delete_course(courseId=None):
    assert courseId is not None
    if len(db(db.course_taken.course_id == courseId).select().as_list()) > 0:
        return "Cannot delete course that you have enrolled in."
    if db(db.course.created_by == auth.user_id).select().as_list() == []:
        return "Cannot delete course that you have not created."
    db(db.course.id == courseId).delete()
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
    curr_user = db(db.auth_user.id == auth.user_id).select().as_list()
    username = curr_user[0]['username']
    db.shared_planner.update_or_insert(user_id=auth.user_id, name=username)
    return "ok"

def add_california_schools():
    for school_name, abbr, state, state_abbr in csu_schools:
        school = db.school(name=school_name)
        if school:
            school.update_record(abbr=abbr, state=state, state_abbr=state_abbr)
        else:
            db.school.insert(name=school_name, abbr=abbr,
                             state=state, state_abbr=state_abbr)

@action('get_shared_users', method="GET")
@action.uses(db, auth.user, url_signer)
def get_shared_users():
    users = db(db.shared_planner.user_id != auth.user_id).select().as_list()
    return dict(users=users)