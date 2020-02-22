var RestDialogueItem = Backbone.Model.extend({
    idAttribute: "RequestCorrelationTag",

    initialize: function () {
    }
});

var RestDialogueCollection = Backbone.Collection.extend({
    model: RestDialogueItem,

    initialize: function () {
        var self = this;

        app.events.on("extension-message:debugger-dialogue:request", function (payload) {
            var item = new RestDialogueItem();
            item.set("request", payload);
            self.add(item);
        });

        app.events.on("extension-message:debugger-dialogue:response", function (payload) {
            var item = self.at(self.length - 1);
            item.set("response", payload);
        });
    }
});