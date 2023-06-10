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

    // assigning grades to their respective point system
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

    // this function calculates the grade point average of the course grades and course credits submitted
    const calculateGpa = courses => {
        const out = courses.reduce((acc, c) => {
            if (gradePoints[c.final_grade]){
                acc.credits += c.credits;
                acc.weightGpa += (c.credits * gradePoints[c.final_grade])
            }
            return acc;
        }, { weightGpa: 0, credits: 0 });
        return out.credits && (out.weightGpa / out.credits).toFixed(2);
    }
    
    // sums up the total credits
    const totalCredits = courses => {
        return courses.reduce((acc, c) => {
            return c.final_grade ? acc + c.credits : acc;
        }, 0);
    }

    //calculates the average grade when submitting the grades along with their weight
    // and the percentage that they got for each assignment category
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

    // function to add rows when wanting to add more assignment categories
    app.addRow = () => {
        app.data.grade_categories.push({assignment: undefined, grade: undefined, weight: undefined, placeholder: "e.g Assignment"})
    }

    // function to delete rows
    app.deleteRow = (category) => {
        app.data.grade_categories = app.data.grade_categories.filter(x => category !== x)
    }

    app.getCourses = () => {
        // Send a GET request to retrieve the user's courses
        axios.get("/courseplanner/get_my_courses").then(response => {
            // Store the retrieved courses in the app's data property
            app.data.courses = response.data.courses_taken
        })
    }

    app.getGradeCategories = (course_taken_id) => {
        // Send a GET request to retrieve grade categories for a specific course taken
        axios.get('/courseplanner/grade_categories', { params: { course_taken_id } }).then(response => {
            // Store the retrieved grade categories and grade in the app's data property
            app.data.grade_categories = response.data.grade_categories;
            app.data.grade = response.data.grade;
        })
    }

    // Save the grade categories for the selected course
    app.saveGradeCategories = () => {
        axios.post('/courseplanner/grade_categories', { 
            grade_categories: app.data.grade_categories, 
            course_taken_id: app.data.selected_course 
        });
    }

    app.submitGrade = async () => {
        // Send a POST request to submit the grade for a selected course
        const response = await axios.post('/courseplanner/submit_grade', { grade: app.data.grade, course_id: app.data.selected_course });

        // Extract the course_id and grade from the response data
        const { course_id, grade } = response.data;

        // Find the corresponding course in the app's data and update its final_grade property
        const course = app.data.courses.find(c => c.id == course_id);
        course.final_grade = grade;
    }

    //
    app.selectCourse = (e) => {
        // Check if a course is selected
        if (e.target.value) {
            // Set the selected_course property in the app's data to the value of the selected course
            app.data.selected_course = e.target.value
            // Call the getGradeCategories function with the selected course to retrieve grade categories
            app.getGradeCategories(e.target.value);
        } else {
            // If no course is selected, reset the selected_course property and clear grade-related data
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