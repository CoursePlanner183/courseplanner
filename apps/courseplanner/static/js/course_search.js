let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {
    // This is the Vue data.
    app.data = {
        ShowSearch: true,
        selectedCourseId: undefined,
        selectedOffering: '',
        selectedEnrollmentStatus: '',
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
        axios.get(`../course/add/${courseId}`, {params: {offering: this.selectedOffering, enrollmentStatus: this.selectedEnrollmentStatus}} )
            .then(response => {
                // Handle the response here (e.g., display a success message)
                const element = this.$refs[courseId+"-add"];
                element.remove();
                this.toggleCourseBox(courseId);
            })
            .catch(error => {
                console.error(error);
            });;
    }

    app.deleteCourse = function (courseId) {
        
        axios.delete(`../course/delete/${courseId}`)
            .then(response => {
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
        toggleCourseBox(courseId) {
            if (this.selectedCourseId === courseId) {
              this.selectedCourseId = null;
              this.selectedOffering = '';
              this.selectedEnrollmentStatus = '';
            } else {
              this.selectedCourseId = courseId;
            }
          },
          openAddCourseBox(courseId,offering) {
            this.selectedCourseId = courseId;
            this.selectedOffering = offering;
            this.selectedEnrollmentStatus = "Enrolled";
          }
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