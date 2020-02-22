var SmartContractsListView = Backbone.View.extend({
    tagName: "div",

    initialize: function () {
        this.childViews = [];
        this.listenTo(this.collection, "update", this.render);
        this.render();

        app.talkToHead("refreshSmartContracts");
    },

    render: function () {
        this.removeChildViews();
        this.createChildViews();
        return this;
    },

    removeChildViews: function () {
        _.each(this.childViews, function (childView) {
            childView.remove();
        });

        this.childViews = [];
    },

    createChildViews: function () {
        this.collection.each(this.createChildView, this);
    },

    createChildView: function (contract) {
        var childView = new SmartContractPanelView({ model: contract });
        childView.render();
        this.$el.append(childView.$el);
        this.childViews.push(childView);
    },

    onClickRefreshSmartContracts: function () {

    }
});