let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {
    // This is the Vue data.
    app.data = {
        ShowSearch: true,
        selectedCourseId: undefined,
        selectedOffering: '',
        courseNumberOption: 'exact',
        selectedEnrollmentStatus: '',
        selectedYearTaken: '',
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
        // Make a request to the server to add the course with params of offering, enrollment status, and year taken
        axios.get(`../course/add/${courseId}`, {params: {offering: this.selectedOffering, enrollmentStatus: this.selectedEnrollmentStatus, yearTaken: this.selectedYearTaken}} )
            .then(response => {
                // response is sucess so remove add button since course can only be enrolled once
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
                // response is sucess so remove entire course from results list
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
            // Resets values for add course popup page and closes current popup
              this.selectedCourseId = null;
              this.selectedOffering = '';
              this.selectedEnrollmentStatus = '';
              this.selectedYearTaken = '';
            } else {
              this.selectedCourseId = courseId;
            }
          },
          openAddCourseBox(courseId,offering) {
            // Sets default values for the add course popup
            this.selectedCourseId = courseId;
            if(offering != null | offering != undefined){
                if(offering.length > 0){
                    this.selectedOffering = offering[0];
                }else{
                    this.selectedOffering = '';
                }
            }
            this.selectedEnrollmentStatus = "Enrolled";
            this.selectedYearTaken = "First Year";
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