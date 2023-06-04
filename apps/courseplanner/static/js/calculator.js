let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {
    // This is the Vue data.
    app.data = {
        grade_categories: [{ assignment: undefined, grade: undefined, weight: undefined, placeholder:"e.g Assignment" }, 
            { assignment: undefined, grade: undefined, weight: undefined, placeholder: "e.g Projects" }, 
            { assignment: undefined, grade: undefined, weight: undefined, placeholder: "e.g Exams" }],
        
        average_grade: undefined,

        courses: []
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {
            e._idx = k++;
        });
        return a;
    };

    app.addRow = () => {
        app.data.grade_categories.push({assignment: undefined, grade: undefined, weight: undefined, placeholder: "e.g Assignment"})
    }

    app.deleteRow = (category) => {
        app.data.grade_categories = app.data.grade_categories.filter(x => category !== x)
    }

    app.getCourses = () => {
        axios.get("/courseplanner/get_my_courses").then(response =>{
            app.data.courses = response.data.courses_taken
        })
    }

    // This contains all the methods.
    app.methods = {
        addRow: app.addRow,
        deleteRow: app.deleteRow
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
        app.getCourses();
    };

    // Call the initializer.
    app.init();
};

// This takes the (empty) app object and initializes it,
// putting all the code in it.
init(app);