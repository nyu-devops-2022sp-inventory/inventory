$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#product_id").val(res.product_id);
        $("#condition").val(res.condition);
        $("#product_name").val(res.product_name);
        $("#quantity").val(res.quantity);
        $("#restock_level").val(res.restock_level);
        $("#reorder_amount").val(res.reorder_amount);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_id").val("");
        $("#condition").val("");
        $("#product_name").val("");
        $("#quantity").val("");
        $("#restock_level").val("");
        $("#reorder_amount").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Pet
    // ****************************************

    $("#create-btn").click(function () {

        let product_id = $("#product_id").val();
        let condition = $("#condition").val();
        let product_name = $("#product_name").val();
        let quantity = $("#quantity").val();
        let restock_level = $("#restock_level").val();
        let reorder_amount = $("#reorder_amount").val();

        let data = {
            "product_id":product_id,
            "product_name":product_name,
            "quantity":quantity,
            "condition":condition,
            "restock_level":restock_level,
            "reorder_amount":reorder_amount
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/inventory",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Pet
    // ****************************************

    // $("#update-btn").click(function () {

    //     let pet_id = $("#pet_id").val();
    //     let name = $("#pet_name").val();
    //     let category = $("#pet_category").val();
    //     let available = $("#pet_available").val() == "true";
    //     let gender = $("#pet_gender").val();
    //     let birthday = $("#pet_birthday").val();

    //     let data = {
    //         "name": name,
    //         "category": category,
    //         "available": available,
    //         "gender": gender,
    //         "birthday": birthday
    //     };

    //     $("#flash_message").empty();

    //     let ajax = $.ajax({
    //             type: "PUT",
    //             url: `/pets/${pet_id}`,
    //             contentType: "application/json",
    //             data: JSON.stringify(data)
    //         })

    //     ajax.done(function(res){
    //         update_form_data(res)
    //         flash_message("Success")
    //     });

    //     ajax.fail(function(res){
    //         flash_message(res.responseJSON.message)
    //     });

    // });

    // ****************************************
    // Retrieve a Pet
    // ****************************************

    // $("#retrieve-btn").click(function () {

    //     let pet_id = $("#pet_id").val();

    //     $("#flash_message").empty();

    //     let ajax = $.ajax({
    //         type: "GET",
    //         url: `/pets/${pet_id}`,
    //         contentType: "application/json",
    //         data: ''
    //     })

    //     ajax.done(function(res){
    //         //alert(res.toSource())
    //         update_form_data(res)
    //         flash_message("Success")
    //     });

    //     ajax.fail(function(res){
    //         clear_form_data()
    //         flash_message(res.responseJSON.message)
    //     });

    // });

    // ****************************************
    // Delete a Pet
    // ****************************************

    // $("#delete-btn").click(function () {

    //     let pet_id = $("#pet_id").val();

    //     $("#flash_message").empty();

    //     let ajax = $.ajax({
    //         type: "DELETE",
    //         url: `/pets/${pet_id}`,
    //         contentType: "application/json",
    //         data: '',
    //     })

    //     ajax.done(function(res){
    //         clear_form_data()
    //         flash_message("Pet has been Deleted!")
    //     });

    //     ajax.fail(function(res){
    //         flash_message("Server error!")
    //     });
    // });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#product_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Pet
    // ****************************************

    // $("#search-btn").click(function () {

    //     let name = $("#pet_name").val();
    //     let category = $("#pet_category").val();
    //     let available = $("#pet_available").val() == "true";

    //     let queryString = ""

    //     if (name) {
    //         queryString += 'name=' + name
    //     }
    //     if (category) {
    //         if (queryString.length > 0) {
    //             queryString += '&category=' + category
    //         } else {
    //             queryString += 'category=' + category
    //         }
    //     }
    //     if (available) {
    //         if (queryString.length > 0) {
    //             queryString += '&available=' + available
    //         } else {
    //             queryString += 'available=' + available
    //         }
    //     }

    //     $("#flash_message").empty();

    //     let ajax = $.ajax({
    //         type: "GET",
    //         url: `/pets?${queryString}`,
    //         contentType: "application/json",
    //         data: ''
    //     })

    //     ajax.done(function(res){
    //         //alert(res.toSource())
    //         $("#search_results").empty();
    //         let table = '<table class="table table-striped" cellpadding="10">'
    //         table += '<thead><tr>'
    //         table += '<th class="col-md-2">ID</th>'
    //         table += '<th class="col-md-2">Name</th>'
    //         table += '<th class="col-md-2">Category</th>'
    //         table += '<th class="col-md-2">Available</th>'
    //         table += '<th class="col-md-2">Gender</th>'
    //         table += '<th class="col-md-2">Birthday</th>'
    //         table += '</tr></thead><tbody>'
    //         let firstPet = "";
    //         for(let i = 0; i < res.length; i++) {
    //             let pet = res[i];
    //             table +=  `<tr id="row_${i}"><td>${pet._id}</td><td>${pet.name}</td><td>${pet.category}</td><td>${pet.available}</td><td>${pet.gender}</td><td>${pet.birthday}</td></tr>`;
    //             if (i == 0) {
    //                 firstPet = pet;
    //             }
    //         }
    //         table += '</tbody></table>';
    //         $("#search_results").append(table);

    //         // copy the first result to the form
    //         if (firstPet != "") {
    //             update_form_data(firstPet)
    //         }

    //         flash_message("Success")
    //     });

    //     ajax.fail(function(res){
    //         flash_message(res.responseJSON.message)
    //     });

    // });

})
