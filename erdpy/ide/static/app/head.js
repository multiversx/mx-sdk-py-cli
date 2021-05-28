function getHead() {
    if (document.location.href.indexOf("vscode") > -1) {
        return new VsCodeHead();
    } else {
        return new BrowserHead();
    }
}

function VsCodeHead() {
    function postMessage(what, payload) {
        window.parent.postMessage({ what: what, payload: payload }, "*");
    }

    function log(payload) {
        postMessage("log", payload);
    }

    window.addEventListener("message", function(event) {
        // Message from vscode webview.
        var data = event.data;
        var what = data.what;
        var payload = data.payload || {};
        
        log(`Received message from vscode: ${what}`);
        app.events.trigger(`extension-message:${what}`, payload);
    });

    return {
        postMessage: postMessage,
        log: log
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