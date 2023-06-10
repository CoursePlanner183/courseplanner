import datetime
import random

from yatl.helpers import A
from py4web import action, request,abort, redirect, URL, Field
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from py4web.utils.form import Form, FormStyleDefault,FormStyleBulma,SelectWidget
from .models import insert_random_courses, get_username,csu_schools,uc_schools
from pydal.validators import *

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth.user, url_signer)
def index():
    student = db(db.student.user_id == auth.user_id).select().as_list()
    if student == []:
        db.student.insert(user_id=auth.user_id)
    student = db(db.student.user_id == auth.user_id).select().as_list()
    if student[0]['major'] is None and student[0]['school_id'] is None:
        redirect(URL('user/profile'))
    courses = db(db.course).select().as_list()
    curr_user = db.auth_user(auth.user_id)
    return dict(
        courses=courses,
        curr_user=curr_user,
        add_course_url=URL('course/add', signer=url_signer),
        edit_course_url=URL('course/edit', signer=url_signer),
        share_courses_url=URL('share_courses', signer=url_signer),
        get_shared_status_url=URL('get_shared_status', signer=url_signer),
    )

@action('course/create', method=["GET", "POST"])
@action.uses('course.html', db, auth.user, url_signer)
def create_course():
    """
    Form for creating a course. Adds in custom class for offering to make it a multi select. 
    Form fields are all the fields in course table.
    return data is:
        form = py4web form generation for adding a course
    """
    form = Form(db.course, deletable=False, formstyle=FormStyleBulma)
    form.structure.find('[name=name]')[0]['_placeholder'] = 'e.g. Web Applications'
    form.structure.find('[name=abbreviation]')[0]['_placeholder'] = 'e.g. CSE'
    form.structure.find('[name=number]')[0]['_placeholder'] = 'e.g. 183'
    form.structure.find('[name=description]')[0]['_placeholder'] = 'e.g. This course introduces the design of Web applications.'
    form.structure.find('[name=credits]')[0]['_placeholder'] = 'e.g. 5'
    form.structure.find('[name=instructor]')[0]['_placeholder'] = 'e.g. Sammy Slug'
    form.structure.find('[name=offering]')[0]['_class'] = 'custom-select'
    form.structure.find('[class=select]')[0]["_class"] = "select is-multiple"
    form.structure.find('[name=year]')[0]['_placeholder'] = 'e.g. 2023'
    if form.accepted:
        redirect(URL("index"))
    return dict(form=form)

@action('course/edit/<courseId:int>', method=["GET", "POST"])
@action.uses('course.html', db, session, auth.user, url_signer)
def edit_course(courseId=None):
    """
    Form generation for editing a course. Takes in courseId which is required and gets course info to display on screen
    Form fields are all the fields in course_taken table.
    return data is:
        form = py4web form generation for editing a course
    """
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

@action('course/taken/edit/<course_takenId:int>', method=["GET", "POST"])
@action.uses('course.html', db, session, auth.user, url_signer)
def edit_course_taken(course_takenId=None):
    """
    Form generation for editing a enrollment in a course. Takes in course_takenId which is required and gets course info to display on screen
    return data is:
        form = py4web form generation for editing a course_taken
    """
    assert course_takenId is not None
    course_taken = db.course_taken[course_takenId]
    if(course_taken.user_id != auth.user_id):
        redirect(URL("course/history"))
    if course_taken is None:
        redirect(URL("course/history"))
    form = Form(db.course_taken,record=course_taken,deletable=False,formstyle=FormStyleBulma,csrf_session=session)
    if form.accepted:
        redirect(URL("course/history"))
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
    """
    Gets all the courses created by the user and returns them as rows.
    return data is:
        rows = query results of all courses created by user
    """
    user = auth.get_user()
    rows = db(db.course.created_by == user["id"]).select()
    for row in rows:
        row["offering"] = ", ".join(row["offering"])
    return dict(rows=rows,get_user_courses_url=URL('course/user/all', signer=url_signer))

@action('course/user/all', method=["GET"])
@action.uses(url_signer.verify(),db, auth.user)
def get_user_courses():
    """
    Gets all the courses created by the user and returns them as rows.
    return data is:
        rows = query results of all courses created by user
    """
    user = auth.get_user()
    rows = db(db.course.created_by == user["id"]).select()
    for row in rows:    
        row["offering"] = ", ".join(row["offering"])
    return dict(rows=rows,)

@action('course/history', method=["GET", "POST"])
@action.uses('course_history.html', db, auth.user, url_signer)
def course_history():
    """
    Gets all the enrollments that the user has and returns then as rows alongside course data.
    return data is:
        rows = query results of all enrollments joined with course table
    """
    user = auth.get_user()
    rows = db(db.course_taken.user_id == user["id"]).select(db.course_taken.ALL, db.course.ALL,
                                                      join=db.course_taken.on(db.course_taken.course_id == db.course.id))
    for row in rows:
        row["course"]["offering"] = ", ".join(row["course"]["offering"])
    return dict(rows=rows)


#controller for user to be able to access their profile and update their profile
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
        redirect(URL('index'))
    return dict()
    
@action("course/search", method=["GET","POST"])
@action.uses('search_course.html',db,session, auth.user)
def search_course():
    """
    Main method for search page. This method will handle the search form and return the results.
    Creates py4web Form 'searchForm''based on course table fields.
    Creates list of field names to be used in YATL template editing
    Handles accepted forms by creating a query based on the form data and returning the results. 
    return data is:
    searchForm = py4web Form object
    DETAIL_FIELDS = list of field names
    results = query results of all courses that match the search criteria
    """
    results = []
    
    #This is so the course option always has a value
    option = 'Exactly'
    if(request.forms.get('number_options') != None):
        option = request.forms.get('number_options')
    
    #Create fields list for form
    fields =[Field("course_name", default=request.forms.get('course_name'), type='string'),
            Field("number_options", default=option, type="string",requires=IS_IN_SET(['Exactly', 'Contains', 'Less than or equal to', 'Greater than or equal to'])),
            Field("course_number", default=request.forms.get('course_number'), type="integer"),
            Field("credits", default=request.forms.get('credits'), type="integer"),
            Field("offering",default=request.forms.get('offering'),type='list:string',requires=IS_IN_SET(['Fall','Winter','Spring','Summer'], multiple=True),multiple=True),
            Field("year", default=request.forms.get('year'), type="integer"),]
    DETAIL_FIELDS = [field.name for field in fields if field.name != "number_options"]
    searchForm = Form(
        fields,
        csrf_session=session,
        formstyle=FormStyleBulma,
    )

    #Edit form variables
    searchForm.structure.find('[name=offering]')[0]['_class'] = 'custom-select'
    searchForm.structure.find('[name=year]')[0]['_type'] = 'number'
    searchForm.structure.find('[name=course_number]')[0]['_type'] = 'number'
    searchForm.custom.submit['_@click'] = 'Search()'  # Add custom inline CSS styles to the button
    searchForm.structure.find('form')[0]['_id']= 'searchFormId'

    #I am not sure why creating the form adds in a whitespace elemnt but it does ant therefore this must be added to delete it
    searchForm.custom.widgets['number_options'][0] =''
    searchForm.custom.widgets['course_number']["_placeholder"] = 'Course #'
    ShowSearch = True
    if searchForm.accepted:
        query = db.course.created_by == auth.user_id

        #Handle the course_name field, look for like or match values in name, abbreviation, and description
        if searchForm.vars['course_name'] != None and searchForm.vars["course_name"] != '':
            keyword = searchForm.vars['course_name']
            query &= (
                (db.course.name.like(f'%{keyword}%')) |
                (db.course.abbreviation.like(f'%{keyword}%')) |
                (db.course.description.like(f'%{keyword}%'))
            )

        #check for course number
        if searchForm.vars['course_number'] != None and searchForm.vars['course_number'] != '':
            number_option = searchForm.vars['number_options']
            number_value = searchForm.vars['course_number']
            
            if number_option == 'Exactly':
                #Ensures results have course number exactly that of the search
                query &= (db.course.number == number_value)
            elif number_option == 'Contains':
                #Ensures results have course number that contains the numbers as in the search box
                query &= (db.course.number.like(f'%{number_value}%'))
            elif number_option == 'Greater than or equal to':
                #Ensures results have course number that is greater than or equal to the number in the search box
                query &= (db.course.number > number_value)
            elif number_option == 'Less than or equal to':
                #Ensures results have course number that is less than or equal to the number in the search box
                query &= (db.course.number < number_value)

        #check for course number
        if searchForm.vars['credits'] != None and searchForm.vars['credits'] != '':
            query &= db.course.credits == searchForm.vars['credits']

        #check for course offering
        if searchForm.vars['offering'] != None and searchForm.vars['offering'] != '':
            query &= db.course.offering == searchForm.vars['offering']

        #check for course year
        if searchForm.vars['year'] != None and searchForm.vars['year'] != '':
            query &= db.course.year == searchForm.vars['year']

        query &= db.course.created_by == auth.user_id
        results = db(query).select()
        for result in results:
            #Check to see if user is owner of course, if so allow course editing
            result["is_owner"] = result["created_by"] == auth.user_id
            #Check to see if user is enrolled in course, if so prevent deletion and also prevent adding to planner
            is_not_enrolled = len(db((db.course_taken.course_id == result["id"]) & (db.course_taken.user_id == auth.user_id)).select().as_list()) == 0
            result["is_not_enrolled"] = is_not_enrolled
    return dict(searchForm=searchForm,results=results,DETAIL_FIELDS=DETAIL_FIELDS)

"""@action("course/add", method="POST")
@action.uses(db, auth.user)
def add_courses():
    courses_selected = request.json.get('courses_selected')
    assert courses_selected is not None
    for courseId in courses_selected:
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
    return "ok
"""

@action("course/add/<courseId:int>", method="GET")
@action.uses(db, session,auth.user)
def add_course(courseId=None):
    """
    add_course() enrolls the user in a course which will then appear in the users planner
    return data:
        none 
    """
    assert courseId is not None
    offeringSelected = request.query.get('offering')
    enrollmentStatus = request.query.get('enrollmentStatus')
    yearTaken = request.query.get('yearTaken')
    if len(db(db.course_taken.course_id == courseId).select().as_list()) > 0:
        return "Course is already taken"
    db.course_taken.insert(
        course_id=courseId,
        user_id = auth.user_id,
        year = yearTaken,
        season = offeringSelected,
        status=enrollmentStatus,
        is_enrolled=True if enrollmentStatus == "Enrolled" else False,
    )
    #redirect(URL("course/search"))
    return "ok"

@action("course/delete/<courseId:int>",method="DELETE")
@action.uses(db, session,auth.user)
def delete_course(courseId=None):
    """
    delete_course() deletes a course that a user has created if no user is enrolled in the course.
    return data:
        none 
    """
    assert courseId is not None
    if len(db(db.course_taken.course_id == courseId).select().as_list()) > 0:
        return "Cannot delete course that you have enrolled in."
    if db(db.course.created_by == auth.user_id).select().as_list() == []:
        return "Cannot delete course that you have not created."
    db(db.course.id == courseId).delete()
    return "ok"

@action("course/taken/delete/<course_takenId:int>", method="DELETE")
@action.uses(db, session,auth.user)
def delete_course_taken(course_takenId=None):
    """
    delete_course_taken() deletes a enrollment from a user and removes it from the planner.
    return data:
        none 
    """
    assert course_takenId is not None
    query = db(db.course_taken.id == course_takenId).select().first()
    if query["user_id"] != auth.user_id:
        redirect(URL('course/history'))
        #return "Cannot delete enrollment that you have not created."
    db(db.course_taken.id == course_takenId).delete()
    redirect(URL('course/history'))

"""
@action("delete_courses", method="POST")
@action.uses(db, auth.user)
def delete_courses():
    courses_delete = request.json.get('courses_delete')
    for courseId in courses_delete:
        db((db.course_taken.course_id == courseId)).delete()
    return "ok"
"""

#controller for the grades/calculator page
@action('grades/calculator', method=["GET", "POST"])
@action.uses('calculator.html', db, auth.user, url_signer)
def calc():
    return dict()


#controller to get the user's courses
@action('get_my_courses')
@action.uses(db, auth.user, url_signer)
def get_my_courses():
    query = (db.course_taken.user_id == auth.user_id) & (db.course_taken.status.belongs(['Enrolled', 'Taken'])) & (
        db.course_taken.course_id == db.course.id)
    courses_taken = db(query).select().as_list()
    courses_taken = [{**c["course"], **c["course_taken"]} for c in courses_taken]
    return dict(courses_taken=courses_taken)


#controller to get user's assignments
@action('grade_categories')
@action.uses(db, auth.user, url_signer)
def get_grade_categories():
    course_taken_id = request.params.get('course_taken_id')
    query = (db.course_grade_categories.user_id == auth.user_id) & (db.course_grade_categories.course_taken_id == course_taken_id)
    grade_categories = db(query).select().as_list()
    
    query = db.course_taken.id == request.params.get('course_taken_id')
    grade = db(query).select().as_list()[0]["final_grade"]
    return dict(grade_categories=grade_categories, grade=grade)


# controller to save user's assignments, weight and percentage
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


#controller to update final grade 
@action('submit_grade', method="POST")
@action.uses(db, auth.user, url_signer)
def submit_grade():
    course_id = request.json.get('course_id')
    grade = request.json.get('grade')
    query = db.course_taken.id == course_id
    db(query).update(final_grade=grade)
    return dict(course_id=course_id, grade=grade)


#controller to get universities for the profile page
@action('universities')
@action.uses(db, auth.user, url_signer)
def universities():
    schools = db(db.school).select().as_list()
    return dict(schools=schools)

#controller to get information of the user on the auth table and student table for the profile page
@action('me')
@action.uses(db, auth.user, url_signer)
def me():
    query = (db.auth_user.id == auth.user_id) & (db.auth_user.id == db.student.user_id)
    x = db(query).select().as_list()[0]
    return { **x["auth_user"], **x["student"] }

#controller for the share.html page
@action('share')
@action.uses('share.html', db, auth.user, url_signer)
def share():
    return dict(
        get_planners_url= URL('get_planners', signer=url_signer),
        get_shared_users_url= URL('get_shared_users', signer=url_signer),
    )

#controller to get information on a student and what they have in their planner
@action('get_planners', method="GET")
@action.uses(db, auth.user, url_signer)
def get_planners():
    '''
    get the full list of courses, courses that the student has taken,
    relevant information about the student and their school.
    ''' 
    user_id = request.params.get('user_id')
    courses = db(db.course).select().as_list()
    courses_taken = db(db.course_taken.user_id == user_id).select(orderby=db.course_taken.year).as_list()
    student = db(db.student.user_id == user_id).select().as_list()
    school = db(db.school.id == student[0]['school_id']).select().as_list()
    curr_user = db(db.auth_user.id == user_id).select().as_list()
    return dict(
        courses=courses,
        courses_taken=courses_taken,
        student=student,
        school=school,
        name=curr_user[0]['username']
    )

#controller to update if a student wishes to share/unshare their planner
@action('share_courses', method="POST")
@action.uses(db, auth.user, url_signer)
def share_courses():
    db(db.student.user_id == auth.user_id).update(shared_planner=request.json.get('newStatus'))
    return "ok"

#controller to get the list of users that shared their planner
@action('get_shared_users', method="GET")
@action.uses(db, auth.user, url_signer)
def get_shared_users():
    # get the users that shared their planner, and also add their name and school to the dict.
    users = db((db.student.user_id != auth.user_id) & (db.student.shared_planner == True)).select().as_list()
    for u in users:
        get_name = db(db.auth_user.id == u['user_id']).select().as_list()
        get_school = db(db.school.id == u['school_id']).select().as_list()
        u['name'] = get_name[0]['username']
        u['school'] = get_school[0]['abbr']
    return dict(users=users)

# get the boolean if student has shared their planner publicly
@action('get_shared_status', method="GET")
@action.uses(db, auth.user, url_signer)
def get_shared_status():
    student = db(db.student.user_id == auth.user_id).select().as_list()
    return dict(status=student[0]['shared_planner'])

#controller for the help.html page
@action('help')
@action.uses('help.html', db, auth.user, url_signer)
def help():
    return dict()