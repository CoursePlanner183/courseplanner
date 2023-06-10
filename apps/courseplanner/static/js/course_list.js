let app = {};

// Enum for seasons
const FilterOptions = {
    None: 0,
    Ascending: 1,
    Descending: 2
};


// Sort the rows array based on the sorting options
const sortRows = (rows, numberFilterOption, yearFilterOption, creditsFilterOption, abbrFilterOption, offeringFilterOption) => {
    const sortedRows = [...rows]; // Create a copy of the original array

    // Sort by number
    if (numberFilterOption === FilterOptions.Ascending) {
        sortedRows.sort((a, b) => a.number - b.number);
    } else if (numberFilterOption === FilterOptions.Descending) {
        sortedRows.sort((a, b) => b.number - a.number);
    }

    // Sort by year
    if (yearFilterOption === FilterOptions.Ascending) {
        sortedRows.sort((a, b) => a.year - b.year);
    } else if (yearFilterOption === FilterOptions.Descending) {
        sortedRows.sort((a, b) => b.year - a.year);
    }

    // Sort by credits
    if (creditsFilterOption === FilterOptions.Ascending) {
        sortedRows.sort((a, b) => a.credits - b.credits);
    } else if (creditsFilterOption === FilterOptions.Descending) {
        sortedRows.sort((a, b) => b.credits - a.credits);
    }

    // Sort by abbreviation
    if (abbrFilterOption === FilterOptions.Ascending) {
        sortedRows.sort((a, b) => a.abbreviation.localeCompare(b.abbreviation));
    } else if (abbrFilterOption === FilterOptions.Descending) {
        sortedRows.sort((a, b) => b.abbreviation.localeCompare(a.abbreviation));
    }

    // Sort by offering
    if (offeringFilterOption === FilterOptions.Ascending) {
        sortedRows.sort((a, b) => a.offering.localeCompare(b.offering));
      } else if (offeringFilterOption === FilterOptions.Descending) {
        sortedRows.sort((a, b) => b.offering.localeCompare(a.offering));
      }

    return sortedRows;
};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {
    // This is the Vue data.
    app.data = {
        rows: [],
        numberFilterOption: FilterOptions.None,
        yearFilterOption: FilterOptions.None,
        creditsFilterOption: FilterOptions.None,
        abbrFilterOption: FilterOptions.None,
        offeringFilterOption: FilterOptions.None,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {
            e._idx = k++;
        });
        return a;
    };


    app.sortByNumber = function () {
        if (app.data.numberFilterOption == FilterOptions.None) {
            app.data.numberFilterOption = FilterOptions.Ascending;
        } else if (app.data.numberFilterOption == FilterOptions.Ascending) {
            app.data.numberFilterOption = FilterOptions.Descending;
        } else if (app.data.numberFilterOption == FilterOptions.Descending) {
            app.data.numberFilterOption = FilterOptions.None;
        }
        app.init();
    };

    app.sortByYear = function () {
        if (app.data.yearFilterOption == FilterOptions.None) {
            app.data.yearFilterOption = FilterOptions.Ascending;
        } else if (app.data.yearFilterOption == FilterOptions.Ascending) {
            app.data.yearFilterOption = FilterOptions.Descending;
        } else if (app.data.yearFilterOption == FilterOptions.Descending) {
            app.data.yearFilterOption = FilterOptions.None;
        }
        app.init();
    };

    app.sortByCredits = function () {
        if (app.data.creditsFilterOption == FilterOptions.None) {
            app.data.creditsFilterOption = FilterOptions.Ascending;
        } else if (app.data.creditsFilterOption == FilterOptions.Ascending) {
            app.data.creditsFilterOption = FilterOptions.Descending;
        } else if (app.data.creditsFilterOption == FilterOptions.Descending) {
            app.data.creditsFilterOption = FilterOptions.None;
        }
        app.init();
    };
    app.sortByAbbr = function () {
        if (app.data.abbrFilterOption == FilterOptions.None) {
            app.data.abbrFilterOption = FilterOptions.Ascending;
        } else if (app.data.abbrFilterOption == FilterOptions.Ascending) {
            app.data.abbrFilterOption = FilterOptions.Descending;
        } else if (app.data.abbrFilterOption == FilterOptions.Descending) {
            app.data.abbrFilterOption = FilterOptions.None;
        }
        app.init();
    };

    app.sortByOffering = function () {
        if (app.data.offeringFilterOption == FilterOptions.None) {
            app.data.offeringFilterOption = FilterOptions.Ascending;
        } else if (app.data.offeringFilterOption == FilterOptions.Ascending) {
            app.data.offeringFilterOption = FilterOptions.Descending;
        } else if (app.data.offeringFilterOption == FilterOptions.Descending) {
            app.data.offeringFilterOption = FilterOptions.None;
        }
        app.init();
    };

    app.getSortIconClass = function (filterOption) {
        switch (filterOption) {
            case FilterOptions.Ascending:
                return "fa fa-sort-up";
            case FilterOptions.Descending:
                return "fa fa-sort-down";
            default:
                return "fa fa-sort";
        }
    };

    // This contains all the methods.
    app.methods = {
        sortByNumber: app.sortByNumber,
        sortByYear: app.sortByYear,
        sortByCredits: app.sortByCredits,
        getSortIconClass: app.getSortIconClass,
        sortByAbbr: app.sortByAbbr,
        sortByOffering: app.sortByOffering, 

    };
    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
    });

    // This initializes it.
    app.init = () => {
        axios.get(get_user_courses_url).then(function (response) {
            tempRows = app.enumerate(response.data.rows);
            app.vue.rows = sortRows(
                tempRows,
                app.data.numberFilterOption,
                app.data.yearFilterOption,
                app.data.creditsFilterOption,
                app.data.abbrFilterOption,
                app.data.offeringFilterOption

            );
        });
    };

    // Call the initializer.
    app.init();
};

// This takes the (empty) app object and initializes it,
// putting all the code in it.
init(app);