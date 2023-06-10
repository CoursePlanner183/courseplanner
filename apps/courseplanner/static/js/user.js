let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {
    // This is the Vue data.
    app.data = {
        schools: [],
        student: {},
    };

    // makes an asynchronous HTTP GET request to the /courseplanner/universities 
    // endpoint using axios, and then assigns the extracted schools data from the 
    // response to the app.data.schools property.
    app.getSchools = async () => {
        const response = await axios.get('/courseplanner/universities');
        app.data.schools = response.data.schools;
    }

    // makes an asynchronous HTTP GET request to the /courseplanner/me endpoint 
    // using axios. It then assigns the extracted data from the response to the 
    // app.data.student property.
    app.getMe = async () => {
        const response = await axios.get('/courseplanner/me');
        app.data.student = response.data;
    }

    // This contains all the methods.
    app.methods = {

    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
    });

    // This initializes it.
    app.init = () => {
        app.getMe();
        app.getSchools();
    };

    // Call the initializer.
    app.init();
};

// This takes the (empty) app object and initializes it,
// putting all the code in it.
init(app);