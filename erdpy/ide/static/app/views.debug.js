var DebugView = Backbone.View.extend({
    events: {
        "change [name='FocusedSmartContract']": "onChangeFocusedContract",
        "click .btn-deploy-contract": "onClickDeploy",
        "click .btn-run-contract": "onClickRun",
        "click .btn-configure-watch": "onClickConfigureWatch",
        "click .btn-refresh-watched": "onRefreshWatchedVariables"
    },

    initialize: function () {
        this.listenTo(this.collection, "update", this.render);
        this.render();
    },

    render: function () {
        this.renderListOfContracts();
        this.renderPanelForContract();
    },

    renderListOfContracts: function () {
        var selectList = this.getListOfContractsElement();
        var selected = selectList.val();

        if (this.collection.length == 0) {
            selectList.prop("disabled", "disabled");
        } else {
            selectList.prop("disabled", false);
        }

        selectList.empty();

        this.collection.each(function (model) {
            var contractFriendlyId = model.get("FriendlyId");
            var option = new Option(contractFriendlyId, contractFriendlyId);
            selectList.append(option);
        });

        if (selected) {
            selectList.val(selected);
        }
    },

    getListOfContractsElement: function () {
        return this.$el.find("[name='FocusedSmartContract']");
    },

    renderPanelForContract: function () {
        var model = this.getFocusedContract();

        if (!model) {
            return;
        }

        var contract = model.toJSON();
        var template = app.underscoreTemplates["DebugPanelForContract"];
        var html = template({ contract: contract });
        this.$el.find(".debug-panel").html(html);
        this.renderVMOutput();
    },

    renderVMOutput: function () {
        var model = this.getFocusedContract();

        if (this.vmOutputView) {
            this.vmOutputView.remove();
        }

        this.vmOutputView = new VMOutputView({
            el: this.$el.find(".vm-output-view"),
            model: model.get("PropertiesOnNodeDebug").LatestRun
        });

        this.vmOutputView.render();
    },

    focusOnSmartContract: function (friendlyId) {
        this.getListOfContractsElement().val(friendlyId);
        this.onChangeFocusedContract();
    },

    onChangeFocusedContract: function () {
        this.renderPanelForContract();
    },

    getFocusedContract: function () {
        var friendlyId = this.getListOfContractsElement().val();

        if (!friendlyId) {
            return null;
        }

        var model = this.collection.get(friendlyId);
        return model;
    },

    onClickDeploy: function () {
        var model = this.getFocusedContract();
        var dialog = new DeployDialog({
            model: model
        });

        dialog.show();
    },

    onClickRun: function () {
        var model = this.getFocusedContract();
        var dialog = new RunDialog({
            model: model
        });

        dialog.show();
    },

    onClickConfigureWatch: function () {
        var model = this.getFocusedContract();
        var dialog = new ConfigureWatchDialog({
            model: model
        });

        dialog.show();
    },

    onRefreshWatchedVariables: function() {
        var model = this.getFocusedContract();
        model.queryWatchedVariables();
    }
});

var VMOutputView = Backbone.View.extend({
    tagName: "div",

    initialize: function () {
        this.render();
    },

    render: function () {
        var template = app.underscoreTemplates["TemplateVMOutput"];
        var html = template({ data: this.model.VMOutput || {} });
        this.$el.html(html);
        return this;
    },
});