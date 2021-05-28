var SmartContractPanelView = Backbone.View.extend({
    tagName: "div",

    events: {
        "click .btn-goto-debug": "onClickGotoDebug",
        "click .btn-goto-debug-on-testnet": "onClickGotoDebugOnTestnet"
    },

    initialize: function () {
        this.listenTo(this.model, "change", this.onModelChange);
    },

    onModelChange: function () {
        this.render();
    },

    render: function () {
        var template = app.underscoreTemplates["TemplateSmartContractPanel"];
        var contract = this.model.toJSON();
        var html = template({ contract: contract });
        this.$el.html(html);

        return this;
    },

    onClickGotoDebug: function () {
        var friendlyId = this.model.get("FriendlyId");
        app.debugView.focusOnSmartContract(friendlyId);
        showView("Debug");
    },

    onClickGotoDebugOnTestnet: function () {
        var friendlyId = this.model.get("FriendlyId");
        app.debugOnTestnetView.focusOnSmartContract(friendlyId);
        showView("DebugOnTestnet");
    }
});