let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        planners: [],
    };    
    
    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };    

    app.getPlanners = function(user_id) {
        axios.get(get_planners_url, {params:{ user_id }}).then(function (response) {
            app.vue.planners = app.enumerate(response.data.courses_taken)
            console.log(app.vue.planners)
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