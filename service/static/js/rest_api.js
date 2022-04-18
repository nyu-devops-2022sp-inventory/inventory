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
    // Create a Product
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
    // Search for Product(s)
    // ****************************************

    $("#search-btn").click(function () {

        // let product_id = $("#product_id").val();
        let condition = $("#condition").val();
        let product_name = $("#product_name").val();

        let queryString = ""

        if (product_name) {
            queryString += 'product_name=' + product_name
        }
        if (condition) {
            if (queryString.length > 0) {
                queryString += '&condition=' + condition
            } else {
                queryString += 'condition=' + condition
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/inventory?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">product_id</th>'
            table += '<th class="col-md-2">product_name</th>'
            table += '<th class="col-md-2">condition</th>'
            table += '<th class="col-md-2">quantity</th>'
            table += '<th class="col-md-2">restock_level</th>'
            table += '<th class="col-md-2">reorder_amount</th>'
            table += '</tr></thead><tbody>'
            let firstProduct = "";
            for(let i = 0; i < res.length; i++) {
                let product = res[i];
                table +=  `<tr id="row_${i}"><td>${product.product_id}</td><td>${product.product_name}</td><td>${product.condition}</td><td>${product.quantity}</td><td>${product.restock_level}</td><td>${product.reorder_amount}</td></tr>`;
                if (i == 0) {
                    firstProduct = product;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstProduct != "") {
                update_form_data(firstProduct)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
