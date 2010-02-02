goog.provide('mirosubs.subtitle.TranscribePanel');

/**
 * @param {Array.<mirosubs.subtitle.EditableCaption>} captions
 * @param {mirosubs.UnitOfWork} unitOfWork Used to track any new captions added 
 *     while this widget is active.
 */
mirosubs.subtitle.TranscribePanel = function(captions, unitOfWork) {
    goog.ui.Component.call(this);

    /**
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
goog.inherits(mirosubs.subtitle.TranscribePanel, goog.ui.Component);
mirosubs.subtitle.TranscribePanel.prototype.createDom = function() {
    mirosubs.subtitle.TranscribePanel.superClass_.createDom.call(this);
    this.keyHandler_ = new goog.events.KeyHandler(this.getElement());
    this.getHandler().listen(this.keyHandler_,
                             goog.events.KeyHandler.EventType.KEY,
                             this.handleKey_);
    for (var i = 0; i < this.captions_.length; i++)
        this.addChild(new mirosubs.subtitle.TranscribePanel.Line_(
            this.captions_[i]), true);
    this.addLine_();
};
mirosubs.subtitle.TranscribePanel.prototype.handleKey_ = function(event) {
    var keyCodes = goog.events.KeyCodes;
    if (event.keyCode == keyCodes.ENTER)
        this.addLine_();
};
mirosubs.subtitle.TranscribePanel.prototype.addLine_ = function() {
    if (this.lastNewLine_ != null) {
        var newEditableCaption = new mirosubs.subtitle.EditableCaption(this.unitOfWork_);
        newEditableCaption.setText(this.lastNewLine_.labelInput.getValue());
        this.captions_.push(newEditableCaption);
        this.lastNewLine_.caption = newEditableCaption;
    }
    //TODO: People might want to insert lines in the middle, 
    // not just in the end of the transcript 
    var currentLine = this.lastNewLine_;

    var newLine = new mirosubs.subtitle.TranscribePanel.Line_();
    newLine.previousLine = currentLine;
    newLine.nextLine = null;

    if (currentLine) currentLine.nextLine = newLine;
    this.lastNewLine_ = newLine;
    this.addChild(this.lastNewLine_, true);
};
mirosubs.subtitle.TranscribePanel.prototype.disposeInternal = function() {
    mirosubs.subtitle.TranscribePanel.superClass_.disposeInternal.call(this);
    if (this.keyHandler_)
        this.keyHandler_.dispose();
};

/**
 * @param {mirosubs.subtitle.EditableCaption} opt_caption Caption for this line.
 */
mirosubs.subtitle.TranscribePanel.Line_ = function(opt_caption, opt_domHelper) {
    goog.ui.Component.call(this, opt_domHelper);
    this.caption = opt_caption;
};
goog.inherits(mirosubs.subtitle.TranscribePanel.Line_, goog.ui.Component);
mirosubs.subtitle.TranscribePanel.Line_.prototype.createDom = function() {
    this.decorateInternal(this.dom_.createElement("div"));
};
mirosubs.subtitle.TranscribePanel.Line_.prototype.decorateInternal = function(element) {
    mirosubs.subtitle.TranscribePanel.Line_.superClass_.decorateInternal.call(this, element);
    this.addChild(this.labelInput = new goog.ui.LabelInput("(silence)"), 
                  true);
    if (this.caption != null && this.caption.getText() != '')
        this.labelInput.setValue(this.caption.getText());
    this.labelInput.LABEL_CLASS_NAME = "mirosubs-label-input-label";
    this.getHandler().listen(this.labelInput.getElement(),
                             goog.events.EventType.KEYUP,
                             this.keyUp_,
                             false, this);
    this.getHandler().listen(this.labelInput.getElement(),
                             goog.events.EventType.KEYDOWN,
                             this.keyDown_,
                             false, this);
    goog.Timer.callOnce(this.labelInput.focusAndSelect, 10, this.labelInput);
};

mirosubs.subtitle.TranscribePanel.Line_.prototype.keyUp_ = function(event) {
    if (this.caption != null)
        this.caption.setText(this.labelInput.getValue());
};

mirosubs.subtitle.TranscribePanel.Line_.prototype.keyDown_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.UP && this.previousLine != null)
        this.previousLine.labelInput.getElement().focus();
    if (event.keyCode == goog.events.KeyCodes.DOWN && this.nextLine != null)
        this.nextLine.labelInput.getElement().focus();
};
