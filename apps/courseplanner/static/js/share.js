let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        planners: [],
        year1: [],
        year2: [],
        year3: [],
        year4: [],
        year5: [],
        year6: [],
        year5Mode: false,
        year6Mode: false,
        users: [],
        searched: [],
        query: "",
        curr_name: "",
        curr_major: "",
        curr_school: "",
        curr_state: "",
        selected_id: -1,
        selected_mode: 0,
        intro_mode: 0,
    };    
    
    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };    

    // method to get information on a student and what they have in their planner and organizes it to be displayed on share.html
    app.getPlanners = function(user_id) {
        let years = [
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
        ]
        let year = "";
        axios.get(get_planners_url, {params:{ user_id }}).then(function (response) {
            app.vue.planners = app.enumerate(response.data.courses_taken)
            let courses = app.enumerate(response.data.courses);
            let student = app.enumerate(response.data.student);
            let school = app.enumerate(response.data.school);
            app.vue.curr_name = response.data.name;
            app.vue.curr_major = student[0]['major'];
            app.vue.curr_school = school[0]['name'];
            app.vue.curr_state = school[0]['state']
            for (let i = 0; i < app.vue.planners.length; i++) {
                year = app.vue.planners[i]['year'];
                let course = null;
                for (let j = 0; j < courses.length; j++) {
                    if (courses[j]['id'] == app.vue.planners[i]['course_id']) {
                        course = courses[j]['name'];
                        break;
                    }
                }
                if (year == "Fifth Year" && !app.vue.year5Mode) {
                    app.vue.year5Mode = true
                }
                if (year == "Sixth Year" && !app.vue.year6Mode) {
                    app.vue.year6Mode = true
                }
                switch (year) {
                    case "First Year":
                        switch (app.vue.planners[i]['season']) {
                            case "Fall":
                                years[0][0] = years[0][0].concat(course, "\n")
                                break;
                            case "Winter":
                                years[0][1] = years[0][1].concat(course, "\n")
                                break;
                            case "Spring":
                                years[0][2] = years[0][2].concat(course, "\n")
                                break;
                            case "Summer":
                                years[0][3] = years[0][3].concat(course, "\n")
                                break;
                        }
                        break;
                    case "Second Year":
                        switch (app.vue.planners[i]['season']) {
                            case "Fall":
                                years[1][0] = years[1][0].concat(course, "\n")
                                break;
                            case "Winter":
                                years[1][1] = years[1][1].concat(course, "\n")
                                break;
                            case "Spring":
                                years[1][2] = years[1][2].concat(course, "\n")
                                break;
                            case "Summer":
                                years[1][3] = years[1][3].concat(course, "\n")
                                break;
                        }
                        break;
                    case "Third Year":
                        switch (app.vue.planners[i]['season']) {
                            case "Fall":
                                years[2][0] = years[2][0].concat(course, "\n")
                                break;
                            case "Winter":
                                years[2][1] = years[2][1].concat(course, "\n")
                                break;
                            case "Spring":
                                years[2][2] = years[2][2].concat(course, "\n")
                                break;
                            case "Summer":
                                years[2][3] = years[2][3].concat(course, "\n")
                                break;
                        }
                        break;
                    case "Fourth Year":
                        switch (app.vue.planners[i]['season']) {
                            case "Fall":
                                years[3][0] = years[3][0].concat(course, "\n")
                                break;
                            case "Winter":
                                years[3][1] = years[3][1].concat(course, "\n")
                                break;
                            case "Spring":
                                years[3][2] = years[3][2].concat(course, "\n")
                                break;
                            case "Summer":
                                years[3][3] = years[3][3].concat(course, "\n")
                                break;
                        }
                        break;
                    case "Fifth Year":
                        switch (app.vue.planners[i]['season']) {
                            case "Fall":
                                years[4][0] = years[4][0].concat(course, "\n")
                                break;
                            case "Winter":
                                years[4][1] = years[4][1].concat(course, "\n")
                                break;
                            case "Spring":
                                years[4][2] = years[4][2].concat(course, "\n")
                                break;
                            case "Summer":
                                years[4][3] = years[4][3].concat(course, "\n")
                                break;
                        }
                        break;
                    case "Sixth Year":
                        switch (app.vue.planners[i]['season']) {
                            case "Fall":
                                years[5][0] = years[5][0].concat(course, "\n")
                                break;
                            case "Winter":
                                years[5][1] = years[5][1].concat(course, "\n")
                                break;
                            case "Spring":
                                years[5][2] = years[5][2].concat(course, "\n")
                                break;
                            case "Summer":
                                years[5][3] = years[5][3].concat(course, "\n")
                                break;
                        }
                        break;
                }
            }
            app.vue.year1 = years[0];
            app.vue.year2 = years[1];
            app.vue.year3 = years[2];
            app.vue.year4 = years[3];
            app.vue.year5 = years[4];
            app.vue.year6 = years[5];
        });
    }

    // method to get the list of users or major that starts with the current query
    app.search = function() {
        let search = app.vue.query.toLowerCase()
        app.vue.searched = []
        if (app.vue.selected_mode == 0) {
            for (let i = 0; i < app.vue.users.length; i++) {
                let lowercase = app.vue.users[i].name.toLowerCase();
                if (lowercase.startsWith(search)) {
                    app.vue.searched.push(app.vue.users[i]);
                }
            }
        }
        else {
            for (let i = 0; i < app.vue.users.length; i++) {
                lowercase = app.vue.users[i].major.toLowerCase();
                if (lowercase.startsWith(search)) {
                    app.vue.searched.push(app.vue.users[i]);
                }
            }
        }
    }

    // This contains all the methods.
    app.methods = {
        getPlanners: app.getPlanners,
        search: app.search,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Todo: get list of users who shared
        axios.get(get_shared_users_url).then(function (response) {
            app.vue.users = app.enumerate(response.data.users);
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);