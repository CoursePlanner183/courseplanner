# Course Planner

### Team Members
| Name | Email |
|------|-------|
| Neeha Ravula | nravula@ucsc.edu |
| Vincent Jay Olandria | volandri@ucsc.edu |
| Jasmin Perez | jpere131@ucsc.edu |
| Colby Frey | csfrey@ucsc.edu |
| Jeffrey Gu | jrgu@ucsc.edu |

### Overview
This web app is a comprehensive course planner that allows students to manage their coursework in a seamless manner. Users can easily add, edit, and delete courses and categorize them by their organized status, whether they have taken the course, plan to take it, or want to take it. This allows for easy management of coursework and ensures that users can meet their academic requirements.

The web app also facilitates collaboration among students, as users can share their coursework with others, find students taking the same class, and make informed decisions about what classes to take. This feature helps create a supportive community of learners and enhances the academic journey.

The grade calculator feature enables users to calculate their final course grade and current GPA based on the courses they have taken. This feature is particularly useful for students who need to maintain a certain GPA or want to track their academic performance.

### Main Pages

GPA Calculator<br>
	^<br>
Login > Course Planner > Course finder (allow user to enter custom course if not in db)<br>
	v<br>
Course plan share page/recommended plans for major<br>

Login Page: Server Side<br>
Course Planner Page: Vue.js/Javascript<br>
Course Plan Share Page/Recommended Plans: Vue.js/Javascript<br>
GPA Calculator: Server Side<br>
Course Finder: Server Side<br>

### Data Organization
There will be a starting amount of 4 tables that we think we will need. A table to hold the user data, course data, the courses that a student is taking and finally a table to hold school information. Students will need a database table of their courses, previously taken and currently taking. There will also be a database table for all available courses that a student can take, and a database table to categorize them by major/minor requirements. Maybe adding a database table of all the schools to categorize them by school as well. There would also be a database table showing recommended/shared plans from other users for collaborations.

Our 4 initial tables are below:
<table>
<tr><td>

|User Table|
|--|
|UserId|
|SchoolId|
|FirstName|
|LastName|
|Email|
|GraduationDate|
 
</td><td>

|School Table|
|--|
|SchoolId|
|SchoolName|
|SchoolAbbreviation|
|SchoolState|
| - |
| - |
  
</td><td>

|Course Table|
|--|
|CourseId|
|SchoolId|
|CourseNumber|
|CourseName|
|CourseTime|
|CourseDays|

</td><td>

|User Course Table|
|--|
|UserId|
|CourseId|
|CurrentlyEnrolled|
|Grade|
| - |
| - |

</td></tr> </table>

### User Stories
1. As a user, I want to add a course so that I can create a custom planner.
2. As a user, I want to edit a course from my course planner so that I could keep track of which courses I end up taking that quarter/semester.
3. As a user, I want to delete a course so I could remove a course that I accidentally added or no longer plan to take.
4. As a user, I want to save my course planner with an account so that I could look at it at a later time.
5. As a user, I want to be able to view my coursework in different categories so that I can stay better organized.
6. As a user, I want to be able to calculate my quarter/semester GPA so that I can track my academic progress.
7. As a user, I want to calculate my course grades so that I can track my academic progress.
8. As a user, I want to calculate my final GPA so that I can see if I am maintaining a certain GPA
9. As a user, I want to be able to share my course planner with other students to help other students plan their classes better.
10. As a user, I want to be able to view course planners that were shared with me so that I can plan my future courses better and build connections through mutual classes.
11. As a user, I want to see recommended courses based on the ones I’ve already taken and the ones that I still need to take so that my course planner includes all the required courses to take for my major.

### Implementation Plan
| Period | User Stories |
|------|-------|
| 1 | 1, 2, 3, 4, 5 |
| 2 | 6, 7, 8 |
| 3 | 9, 10, 11 |


