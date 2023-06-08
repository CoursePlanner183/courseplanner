let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {
    // This is the Vue data.
    app.data = {
        ShowSearch: true,
    };

    app.Search = () => {
        // Get the form element
        var form = document.getElementById('searchFormId');
        // Make an AJAX POST request to the form action URL
        form.submit()
    }
    app.OpenSearch = () => {
        app.vue.ShowSearch = true;
    }
    app.addCourse = function (courseId) {
        axios.get(`../course/add/${courseId}`)
            .then(response => {
                // Handle the response here (e.g., display a success message)
                console.log(response.data);
                const element = this.$refs[courseId+"-add"];
                element.remove();
            })
            .catch(error => {
                console.error(error);
            });;
    }

    app.deleteCourse = function (courseId) {
        
        axios.delete(`../course/delete/${courseId}`)
            .then(response => {
                console.log(response.data);
                const element = this.$refs[courseId+"-card"];
                element.remove();
            })
            .catch(error => {
                console.error(error);
            });;
    }
    
    // This contains all the methods.
    app.methods = {
        Search: app.Search,
        OpenSearch: app.OpenSearch,
        addCourse: app.addCourse,
        deleteCourse: app.deleteCourse,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
    });


    // This initializes it.
    app.init = () => {
        console.log("SS is " + app.vue.ShowSearch);
    };

    // Call the initializer.
    app.init();
};

// This takes the (empty) app object and initializes it,
// putting all the code in it.
init(app);