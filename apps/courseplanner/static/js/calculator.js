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

        selected_course: undefined,

        total_credits: undefined,

        gpa: undefined,
    };

    const gradePoints = {
        'A+': 4,
        'A': 4,
        'A-': 3.7,
        'B+': 3.3,
        'B': 3,
        'B-': 2.7,
        'C+': 2.3,
        'C': 2,
        'C-': 1.7,
        'D+': 1.3,
        'D': 1,
        'D-': 0.7,
        'F': 0,
    }

    const calculateGpa = courses => {
        const out = courses.reduce((acc, c) => {
            acc.credits += c.credits;
            acc.weightGpa += (c.credits * gradePoints[c.final_grade])
            return acc;
        }, { weightGpa: 0, credits: 0 });
        return out.weightGpa / out.credits;
    }
    
    const totalCredits = courses => {
        return courses.reduce((acc, c) => {
            return acc + c.credits;
        }, 0);
    }

    const calculateAvgGrade = (gradeCategories) => {
        const out = gradeCategories.reduce((acc, x) => {
            if (!isNaN(x.grade) && !isNaN(x.weight)) {
                acc.weightedGrade += (Number(x.weight) * Number(x.grade));
                acc.weightTotal += Number(x.weight);
            }
            return acc;
        }, { weightedGrade: 0, weightTotal: 0 });
        return out.weightTotal !== 0 ? out.weightedGrade / out.weightTotal : 0;
    }


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
        axios.get("/courseplanner/get_my_courses").then(response => {
            app.data.courses = response.data.courses_taken
        })
    }

    app.getGradeCategories = (course_taken_id) => {
        axios.get('/courseplanner/grade_categories', { params: { course_taken_id } }).then(response => {
            app.data.grade_categories = response.data.grade_categories;
            app.data.grade = response.data.grade;
        })
    }

    app.saveGradeCategories = () => {
        axios.post('/courseplanner/grade_categories', { 
            grade_categories: app.data.grade_categories, 
            course_taken_id: app.data.selected_course 
        });
    }

    app.submitGrade = async () => {
        const response = await axios.post('/courseplanner/submit_grade', { grade: app.data.grade, course_id: app.data.selected_course });
        const { course_id, grade } = response.data;
        const course = app.data.courses.find(c => c.id == course_id);
        course.final_grade = grade;
    }

    app.selectCourse = (e) => {
        if (e.target.value) {
            app.data.selected_course = e.target.value
            app.getGradeCategories(e.target.value);
        } else {
            app.data.selected_course = undefined;
            app.data.grade_categories = [];
            app.data.grade = undefined;
        }
    }

    // This contains all the methods.
    app.methods = {
        addRow: app.addRow,
        deleteRow: app.deleteRow,
        selectCourse: app.selectCourse,
        submitGrade: app.submitGrade,
        saveGradeCategories: app.saveGradeCategories,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
        watch: {
            courses: {
                handler: (newValue) => {
                    app.data.total_credits = totalCredits(newValue);
                    app.data.gpa = calculateGpa(newValue);
                },
                deep: true
            },

            grade_categories: {
                handler: (newValue) => {
                    app.data.average_grade = calculateAvgGrade(newValue);
                },
                deep: true
            }
        }
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