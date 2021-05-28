var ConfigureWatchDialog = Backbone.View.extend({
    tagName: "div",
    className: "modal",

    events: {
        "shown.bs.modal": "onBootstrapModalShown",
        "hidden.bs.modal": "onBootstrapModalHidden",
        "click .btn-add-watch": "onClickAddWatch",
        "click .btn-update-watch": "onClickUpdateWatch",
        "click .btn-delete-watch": "onClickDeleteWatch",
        "click .btn-submit": "onClickSubmit"
    },

    initialize: function (options) {
        this.onTestnet = options.onTestnet;
        this.listenTo(this.model, "change", this.onModelChange);
        this.render();
    },

    onModelChange: function () {
        this.renderWatchedVariables();
    },

    render: function () {
        var template = app.underscoreTemplates["TemplateConfigureWatchDialog"];
        var contract = this.model.toJSON();
        var html = template({ contract: contract, onTestnet: this.onTestnet });
        this.$el.html(html);

        if (!$.contains(document, this.el)) {
            this.$el.appendTo("body");
            this.$el.modal({ show: false });
        }

        this.renderWatchedVariables();

        return this;
    },

    renderWatchedVariables: function () {
        var template = app.underscoreTemplates["TemplateWatchedVariables"];
        var contract = this.model.toJSON();
        var html = template({ contract: contract, onTestnet: this.onTestnet });
        this.$el.find(".watched-variables-container").html(html);
    },

    show: function () {
        this.$el.modal("show");
    },

    close: function () {
        this.$el.modal("hide");
    },

    onBootstrapModalShown: function () {
    },

    onBootstrapModalHidden: function () {
        this.$el.data('modal', null);
        this.remove();
    },

    onClickAddWatch: function () {
        this.model.addWatchedVariable({
            onTestnet: this.onTestnet
        });
    },

    onClickUpdateWatch: function (event) {
        var variableElement = $(event.currentTarget).closest(".watched-variable");
        var index = variableElement.attr("data-index");

        var name = variableElement.find("[name='VariableName']").val();
        var functionName = variableElement.find("[name='FunctionName']").val();
        var functionArguments = variableElement.find("[name='Args']").val().split("\n");

        this.model.updateWatchedVariable({
            onTestnet: this.onTestnet,
            index: index,
            name: name,
            functionName: functionName,
            arguments: functionArguments
        });
    },

    onClickDeleteWatch: function (event) {
        var variableElement = $(event.currentTarget).closest(".watched-variable");
        var index = variableElement.attr("data-index");

        this.model.deleteWatchedVariable({
            onTestnet: this.onTestnet,
            index: index
        });
    },

    onClickSubmit: function () {
    }
});
