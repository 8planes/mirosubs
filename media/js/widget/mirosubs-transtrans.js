goog.provide('mirosubs.trans.TransWidget');

/**
 * @param {Array.<mirosubs.trans.EditableCaption>} captions
 * @param {mirosubs.UnitOfWork} unitOfWork Used to track any new captions added 
 *     while this widget is active.
 */
mirosubs.trans.TransWidget = function(captions, unitOfWork, opt_domHelper) {
    goog.ui.Component.call(this, opt_domHelper);

    /**
     * Event handler for this object.
     * @type {goog.events.EventHandler}
     * @private
     */
    this.eventHandler_ = new goog.events.EventHandler(this);

    /**
     * Keyboard handler for this object.
     *
     * @type {goog.events.KeyHandler?}
     * @private
     */
    this.keyHandler_ = null;
    this.captions_ = captions;
    this.unitOfWork_ = unitOfWork;
    this.lastNewLine_ = null;
};
goog.inherits(mirosubs.trans.TransWidget, goog.ui.Component);
mirosubs.trans.TransWidget.prototype.createDom = function() {
    this.decorateInternal(this.getDomHelper().createElement('div'));
};
mirosubs.trans.TransWidget.prototype.decorateInternal = function(element) {
    mirosubs.trans.TransWidget.superClass_.decorateInternal.call(this, element);
    this.keyHandler_ = new goog.events.KeyHandler(this.getElement());
    this.eventHandler_.listen(this.keyHandler_,
                              goog.events.KeyHandler.EventType.KEY,
                              this.handleKey_);
    for (var i = 0; i < this.captions_.length; i++)
        this.addChild(new mirosubs.trans.TransWidget.Line_(this.captions_[i]), true);
    this.addLine_();
};
mirosubs.trans.TransWidget.prototype.handleKey_ = function(event) {
    var keyCodes = goog.events.KeyCodes;
    if (event.keyCode == keyCodes.ENTER)
        this.addLine_();
};
mirosubs.trans.TransWidget.prototype.addLine_ = function() {
    if (this.lastNewLine_ != null) {
        var newEditableCaption = new mirosubs.trans.EditableCaption(this.unitOfWork_);
        newEditableCaption.setText(this.lastNewLine_.labelInput.getValue());
        this.captions_.push(newEditableCaption);
        this.lastNewLine_.caption = newEditableCaption;
    }
    this.lastNewLine_ = new mirosubs.trans.TransWidget.Line_();
    this.addChild(this.lastNewLine_, true);
};
mirosubs.trans.TransWidget.prototype.disposeInternal = function() {
    mirosubs.trans.TransWidget.superClass_.disposeInternal.call(this);
    this.eventHandler_.dispose();
    if (this.keyHandler_)
        this.keyHandler_.dispose();
};

/**
 * @param {mirosubs.trans.EditableCaption} opt_caption Caption for this line.
 */
mirosubs.trans.TransWidget.Line_ = function(opt_caption, opt_domHelper) {
    goog.ui.Component.call(this, opt_domHelper);
    this.caption = opt_caption;
};
goog.inherits(mirosubs.trans.TransWidget.Line_, goog.ui.Component);
mirosubs.trans.TransWidget.Line_.prototype.createDom = function() {
    this.decorateInternal(this.dom_.createElement("div"));
};
mirosubs.trans.TransWidget.Line_.prototype.decorateInternal = function(element) {
    mirosubs.trans.TransWidget.Line_.superClass_.decorateInternal.call(this, element);
    this.addChild(this.labelInput = new goog.ui.LabelInput("(silence)"), 
                  true);
    if (this.caption != null && this.caption.getText() != '')
        this.labelInput.setValue(this.caption.getText());
    this.labelInput.LABEL_CLASS_NAME = "mirosubs-label-input-label";
    goog.events.listen(this.labelInput.getElement(),
                       goog.events.EventType.KEYUP,
                       this.keyUp_,
                       false, this);
    goog.Timer.callOnce(this.labelInput.focusAndSelect, 10, this.labelInput);
};
mirosubs.trans.TransWidget.Line_.prototype.keyUp_ = function(event) {
    if (this.caption != null)
        this.caption.setText(this.labelInput.getValue());
};