let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {
    // This is the Vue data.
    app.data = {
    };

    app.deleteCourseTaken = function (course_takenId) {
        
        axios.delete(`../course/taken/delete/${course_takenId}`)
            .then(response => {
                location.reload();
            })
            .catch(error => {
                console.error(error);
            });;
    }
    // This contains all the methods.
    app.methods = {
        deleteCourseTaken: app.deleteCourseTaken,

    };
    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
    });

    // This initializes it.
    app.init = () => {
    };

    // Call the initializer.
    app.init();
};

// This takes the (empty) app object and initializes it,
// putting all the code in it.
init(app);