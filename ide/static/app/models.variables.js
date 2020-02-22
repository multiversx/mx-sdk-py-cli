var VariablesModel = Backbone.Model.extend({
    initialize: function () {
        var self = this;

        app.talkToHead("variables-refresh", {});

        app.events.on("extension-message:variables-refresh", function (payload) {
            self.set(payload);
        });
    },

    save: function (json) {
        app.talkToHead("variables-save", { json: json });
    }
});
