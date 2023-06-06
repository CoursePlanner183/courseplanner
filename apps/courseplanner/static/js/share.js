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
    };    
    
    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };    

    app.getPlanners = function(user_id) {
        let years = [
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""]
        ]
        let currentYear = Number.NEGATIVE_INFINITY
        let year = 0;

        axios.get(get_planners_url, {params:{ user_id }}).then(function (response) {
            app.vue.planners = app.enumerate(response.data.courses_taken)
            let courses = app.enumerate(response.data.courses);
            for (let i = 0; i < app.vue.planners.length; i++) {
                if (app.vue.planners[i]['year'] > currentYear) {
                    year+=1;
                    currentYear = app.vue.planners[i]['year'];
                }
                let course = null;
                for (let j = 0; j < courses.length; j++) {
                    if (courses[j]['id'] == app.vue.planners[i]['course_id']) {
                        course = courses[j]['name'];
                        
                        break;
                    }
                }
                
                switch (year) {
                    case 1:
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
                    case 2:
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
                    case 3:
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
                    case 4:
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
                }
            }
            console.log(years)
            app.vue.year1 = years[0]
            app.vue.year2 = years[1]
            app.vue.year3 = years[2]
            app.vue.year4 = years[3]
            console.log(app.vue.year1)
            console.log(app.vue.year2)
            console.log(app.vue.year3)
            console.log(app.vue.year4)
            //Todo add functionality
        });
    }

    // This contains all the methods.
    app.methods = {
        getPlanners: app.getPlanners
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
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);