var VariablesView = Backbone.View.extend({
    events: {
        "click .btn-submit": "onClickSubmit"
    },

    initialize: function () {
        this.listenTo(this.model, "change", this.onModelChange);
        this.render();
    },

    onModelChange: function () {
        this.render();
    },
    
    render: function() {
        this.$el.find("textarea").val(this.model.get("json"));
    },

    onClickSubmit: function () {
        let json = this.$el.find("textarea").val();
        this.model.save(json);
    }
});