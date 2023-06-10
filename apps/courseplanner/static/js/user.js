let app = {};

let init = (app) => {
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

    app.methods = {

    };

    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
    });

    app.init = () => {
        app.getMe();
        app.getSchools();
    };

    app.init();
};


init(app);