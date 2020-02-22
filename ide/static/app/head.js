function getHead() {
    if (window.acquireVsCodeApi) {
        return new VsCodeHead();
    } else {
        return new BrowserHead();
    }
}

function VsCodeHead() {
    var vscode = window.acquireVsCodeApi();

    function postMessage(what, payload) {
        vscode.postMessage({ what: what, payload: payload });
    }

    return {
        postMessage: postMessage
    }
}

function BrowserHead() {
    function postMessage(what, payload) {
        if (what == "refreshSmartContracts") {

        } else if (what == "variables-refresh") {
            refreshSmartContracts();
        } else {
            throw new Error(`Unknown message: ${what}.`);
        }
    }

    function refreshSmartContracts() {
        $.ajax({
            type: "GET",
            url: "/workspace/contracts",
            success: function (response) {
                window.postMessage({ what: "refreshSmartContracts", payload: response.data });
            },
            dataType: "json"
        });
    }

    return {
        postMessage: postMessage
    }
}

// $(function () {
//     var data = JSON.stringify({});

//     $.ajax({
//         type: "POST",
//         url: "/contracts/deploy",
//         data: data,
//         contentType: 'application/json; charset=UTF-8',
//         success: function() {

//         },
//         dataType: "json"
//     });
// })