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

        grade: undefined,

        courses: [],
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

    app.getGradeCategories = (course_id, course_taken_id) => {
        axios.get('/courseplanner/get_grade_categories', { params: { course_id, course_taken_id } }).then(response => {
            app.data.grade_categories = response.data.grade_categories;
            app.data.grade = response.data.grade;
            app.data.average_grade = app.data.grade_categories.reduce((acc, cur) => {
                return acc + (cur.weight * cur.grade);
            }, 0);
        })
    }

    app.submitGrade = async () => {
        const response = await axios.post('/courseplanner/submit_grade', { grade: app.data.grade, course_id: app.data.selected_course });
        console.log(response);
    }

    app.selectCourse = (e) => {
        app.data.selected_course = app.data.courses.find(x => x.course_id == e.target.value).id;
        app.getGradeCategories(e.target.value, app.data.selected_course);
    }

    // This contains all the methods.
    app.methods = {
        addRow: app.addRow,
        deleteRow: app.deleteRow,
        selectCourse: app.selectCourse,
        submitGrade: app.submitGrade
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