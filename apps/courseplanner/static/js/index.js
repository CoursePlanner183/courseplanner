// This will be the object that will contain the Vue attributes
// and be used to initialize it.



let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {


    // This is the Vue data.
    app.data = {
        courses: [],
        selectedCourses: [],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => { e._idx = k++; });
        return a;
    };
    app.addcourses = async function (courseId) {
        await axios.post("../course/add", { courses_selected: app.vue.selectedCourses}).then(function (res) {
            axios.get("../get_courses").then(function (response) {
                app.vue.courses = app.enumerate(response.data.courses);
            });
            app.vue.selectedCourses = [];
        })
    };

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        addcourses: app.addcourses,
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
            console.log(app.enumerate(response.data.courses));
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code in it. 
init(app);

