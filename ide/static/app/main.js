$(function () {
    var data = JSON.stringify({});

    $.ajax({
        type: "POST",
        url: "/contracts/deploy",
        data: data,
        contentType: 'application/json; charset=UTF-8',
        success: function() {

        },
        dataType: "json"
    });
})