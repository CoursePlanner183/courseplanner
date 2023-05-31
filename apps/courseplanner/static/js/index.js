// This will be the object that will contain the Vue attributes
// and be used to initialize it.



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
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => { e._idx = k++; });
        return a;
    };


    //  Adds course to course_taken then reloads page to update
    app.addcourses = async function () {
        axios.post(add_course_url, {courses_selected: app.vue.selectedCourses}).then(function (res) {
            app.vue.selectedCourses = [];
            location.reload();
        })
    };

    app.deleteCourses = async function () {
        axios.post(delete_course_url, {courses_delete: app.vue.selectedDelete}).then(function(response) {
            app.vue.selectedDelete = [];
            location.reload();
        })
    };


    //  Checks if there are courses to add to planner. If there are, then adds courses and years.
    app.updatePlanner = function () {
        if (app.vue.courses_taken.length == 0) {
            console.log("No courses taken")
        } else {
            document.getElementById("table").hidden = false;
            document.getElementById("no_table").hidden = true;

            let lowest_year = Number.MAX_VALUE;
            for (index in app.vue.courses_taken){
                courseid = app.vue.courses_taken[index].id;

                /// Finds course from courses
                course = null;
                for (index in app.vue.courses) {
                    if (app.vue.courses[index].id == courseid) {
                        course = app.vue.courses[index];
                    }
                };
                if (course.year < lowest_year) {lowest_year = course.year};
            }

            //  Adds years to planner
            document.getElementById("first_year").firstChild.innerHTML = lowest_year
            document.getElementById("second_year").firstChild.innerHTML = lowest_year + 1
            document.getElementById("third_year").firstChild.innerHTML = lowest_year + 2
            document.getElementById("fourth_year").firstChild.innerHTML = lowest_year + 3

            // Adds courses to planner
            for (index in app.vue.courses_taken){
                courseid = app.vue.courses_taken[index].id;

                // Finds course from courses
                course = null;
                for (index in app.vue.courses) {
                    if (app.vue.courses[index].id == courseid) {
                        course = app.vue.courses[index];
                    }
                };
                
                //  Offering starts at 1 because first column is empty
                let offering = null;
                switch (course.offering) {
                    case "Fall" :
                        offering = 1;
                        break;
                    case "Winter" :
                        offering = 2;
                        break;
                    case "Spring" :
                        offering = 3;
                        break;
                    case "Summer" :
                        offering = 4;
                        break;
                }

                // Creates course element and adds to planner
                let course_element = document.createElement("p");
                course_element.innerHTML = course.name;
                document.getElementById("planner_body").children[course.year-lowest_year].children[offering].append(course_element)
            }
        }
    };

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        addcourses: app.addcourses,
        updatePlanner: app.updatePlanner,
        deleteCourses: app.deleteCourses,
    };


    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
    });


    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        axios.get("../get_courses").then(function (response) {
            app.vue.courses = app.enumerate(response.data.courses);
            console.log("courses", app.enumerate(response.data.courses));
            app.vue.courses_taken = app.enumerate(response.data.courses_taken);
            console.log("courses_taken", app.enumerate(response.data.courses_taken));

            // Updates Planner
            app.vue.updatePlanner();
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);
