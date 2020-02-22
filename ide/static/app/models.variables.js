var VariablesModel = Backbone.Model.extend({
    initialize: function () {
        var self = this;

        app.talkToVscode("variables-refresh", {});

        app.events.on("extension-message:variables-refresh", function (payload) {
            self.set(payload);
        });
    },

    save: function (json) {
        app.talkToVscode("variables-save", { json: json });
    }
});
