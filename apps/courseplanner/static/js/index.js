let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {
    // This is the Vue data.
    app.data = {
        id: 0,
        courses: [],
        courses_taken: [],
        selectedCourses: [],
        deleteMode: false,
        selectedDelete: [],
        curr_user: {},
        shared_status: false,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {
            e._idx = k++;
        });
        return a;
    };

    // Adds course to course_taken then reloads page to update
    app.addcourses = async function() {
        axios.post(add_course_url, { courses_selected: app.vue.selectedCourses }).then(function(res) {
            app.vue.selectedCourses = [];
            app.init(); // Reload the data after adding courses
        });
    };

    app.deleteCourses = function() {
        axios.post(delete_course_url, { courses_delete: app.vue.selectedDelete }).then(function(res) {
            app.vue.selectedDelete = [];
            app.init(); // Reload the data after deleting courses
        });
    };

    // Checks if there are courses to add to planner. If there are, then adds courses and years.
    app.updatePlanner = function() {
        if (app.vue.courses_taken.length == 0) {
            document.getElementById("table").style.visibility = "hidden";
            document.getElementById("no_table").style.visibility = "visible";
        } else {
            document.getElementById("table").style.visibility = "visible";
            document.getElementById("no_table").style.visibility = "hidden";

            // Minimum of four years in planner
            while (document.getElementById("planner_body").childElementCount < 4) {
                app.add_year();
            }

            // Hides Add Year btn if there are 6 years. Hides Delete Year btn if there are 4 years
            if (document.getElementById("planner_body").childElementCount == 4) {
                document.getElementById("delete_year_btn").style.visibility = "hidden";
            } else if (document.getElementById("planner_body").childElementCount == 6) {
                document.getElementById("add_year_btn").style.visibility = "hidden";
            }

            // Adds course to planner
            for (index in app.vue.courses_taken) {
                // offering starts at 1 because the first column is empty
                let offering = null;
                switch (app.vue.courses_taken[index].season) {
                    case "Fall":
                        offering = 1;
                        break;
                    case "Winter":
                        offering = 2;
                        break;
                    case "Spring":
                        offering = 3;
                        break;
                    case "Summer":
                        offering = 4;
                        break;
                }

                // year_taken starts at 1 because the first column is year title
                let year_taken = null;
                switch (app.vue.courses_taken[index].year) {
                    case "First Year":
                        year_taken = 1;
                        break;
                    case "Second Year":
                        year_taken = 2;
                        break;
                    case "Third Year":
                        year_taken = 3;
                        break;
                    case "Fourth Year":
                        year_taken = 4;
                        break;
                    case "Fifth Year":
                        year_taken = 5;
                        break;
                    case "Sixth Year":
                        year_taken = 6;
                        break;
                }

                // Adds years if there isn't enough years/rows in planner
                while (document.getElementById("planner_body").childElementCount < year_taken) {
                    app.add_year();
                }

                // Finds course from courses
                courseid = app.vue.courses_taken[index].course_id;
                course = null;
                for (index in app.vue.courses) {
                    if (app.vue.courses[index].id == courseid) {
                        course = app.vue.courses[index];
                    }
                }

                // Creates a course element and adds it to the planner
                let course_element = document.createElement("p");
                course_element.innerHTML = course.name;
                document.getElementById("planner_body").children[year_taken-1].children[offering].append(course_element);
            }

        }
    };

    // Adds a year to planner. Maximum of 6 years. Adjusts Add/Delete Year btn accordingly
    app.add_year = function() {
        let template_clone = document.getElementById("year_template").firstChild.firstChild.cloneNode(true);
        template_clone.firstChild.textContent = "Another Year"
        document.getElementById("planner_body").appendChild(template_clone);

        //  Adds year name to planner
        switch (document.getElementById("planner_body").childElementCount) {
            case 1:
                document.getElementById("planner_body").lastElementChild.firstChild.textContent = "First Year"
                break;
            case 2:
                document.getElementById("planner_body").lastElementChild.firstChild.textContent = "Second Year"
                break;
            case 3:
                document.getElementById("planner_body").lastElementChild.firstChild.textContent = "Third Year"
                break;
            case 4:
                document.getElementById("planner_body").lastElementChild.firstChild.textContent = "Fourth Year"
                break;
            case 5:
                document.getElementById("planner_body").lastElementChild.firstChild.textContent = "Fifth Year"
                break;
            case 6:
                document.getElementById("planner_body").lastElementChild.firstChild.textContent = "Sixth Year"
                break;
        }

        if (document.getElementById("planner_body").childElementCount > 4) {
            document.getElementById("delete_year_btn").style.visibility = "visible";
        }
        if (document.getElementById("planner_body").childElementCount == 6) {
            document.getElementById("add_year_btn").style.visibility = "hidden";
        }
    };

    // Deletes a year to planner. Minimum of 4 years. Adjusts Add/Delete Year btn accordingly
    app.delete_year = function() {

        //  Exit function if there is class in row to be deleted
        for (let i = 1; i<document.getElementById("planner_body").lastElementChild.childElementCount; i++) {
            if (document.getElementById("planner_body").lastElementChild.children[i].innerHTML != "") {
                alert("There is a course in the row you are trying to delete. Please delete the course first. You can delete a course in course enrollment history")
                return;
            }
        }

        document.getElementById("planner_body").removeChild(document.getElementById("planner_body").lastElementChild);
        if (document.getElementById("planner_body").childElementCount < 6) {
            document.getElementById("add_year_btn").style.visibility = "visible";
        }
        if (document.getElementById("planner_body").childElementCount == 4) {
            document.getElementById("delete_year_btn").style.visibility = "hidden";
        }
    };

    // Set a student's shared_planner to true/false based on the previous status.
    app.share_courses = async function() {
        axios.post(share_courses_url, {
            newStatus: !app.vue.shared_status
        }).then(function(response) {
            app.vue.shared_status = !app.vue.shared_status;
        })
    };

    // This contains all the methods.
    app.methods = {
        addcourses: app.addcourses,
        updatePlanner: app.updatePlanner,
        deleteCourses: app.deleteCourses,
        share_courses: app.share_courses,
        add_year: app.add_year,
        delete_year: app.delete_year,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
    });

    // This initializes it.
    app.init = () => {
        // Put here any initialization code.
        app.vue.curr_user = {}; // Initialize curr_user object

        axios.get("../get_courses").then(function(response) {
            app.vue.courses = app.enumerate(response.data.courses);
            app.vue.courses_taken = app.enumerate(response.data.courses_taken);

            // Updates Planner
            app.vue.updatePlanner();
        });
        axios.get("../get_user").then(function(response) {
            app.vue.curr_user.first_name = response.data.first_name;
            app.vue.curr_user.last_name = response.data.last_name;

            // ...
        });

        //get bool of if user has shared their planner
        axios.get(get_shared_status_url).then(function (response) {
            app.vue.shared_status = response.data.status
        });
    };


    // Call the initializer.
    app.init();
};

// This takes the (empty) app object and initializes it,
// putting all the code in it.
init(app);