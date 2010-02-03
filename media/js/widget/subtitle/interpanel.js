goog.provide('mirosubs.subtitle.InterPanel');

mirosubs.subtitle.InterPanel = function(message, opt_addClassName) {
    goog.ui.Component.call(this);
    this.message_ = message;
    this.addClassName_ = opt_addClassName;
};
goog.inherits(mirosubs.subtitle.InterPanel, goog.ui.Component);
mirosubs.subtitle.InterPanel.prototype.createDom = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var helpLi = mirosubs.subtitle.Util.createHelpLi(this.getDomHelper(),
                                                     [this.message_]);
    this.setElementInternal($d('ul', {'className':'mirosubs-titlesList'},
                               helpLi));
    if (this.addClassName_)
        goog.dom.classes.add(this.getElement(), this.addClassName_);
};