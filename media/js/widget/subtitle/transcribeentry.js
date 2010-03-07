goog.provide('mirosubs.subtitle.TranscribeEntry');

mirosubs.subtitle.TranscribeEntry = function(videoPlayer) {
    goog.ui.Component.call(this);
    this.videoPlayer_ = videoPlayer;
};
goog.inherits(mirosubs.subtitle.TranscribeEntry, goog.ui.Component);
mirosubs.subtitle.TranscribeEntry.prototype.createDom = function() {
    mirosubs.subtitle.TranscribeEntry.superClass_.createDom.call(this);
    this.getElement().setAttribute('class', 'mirosubs-transcribeControls');
    this.addChild(this.labelInput_ = new goog.ui.LabelInput(
        'Type subtitle and press enter'), true);
    this.labelInput_.LABEL_CLASS_NAME = 'mirosubs-label-input-label';
    goog.dom.classes.add(this.labelInput_.getElement(), 'trans');
};
mirosubs.subtitle.TranscribeEntry.prototype.enterDocument = function() {
    mirosubs.subtitle.TranscribeEntry.superClass_.enterDocument.call(this);
    this.keyHandler_ = new goog.events.KeyHandler(this.labelInput_.getElement());
    this.getHandler().listen(this.keyHandler_,
                             goog.events.KeyHandler.EventType.KEY,
                             this.handleKey_);
    this.getHandler().listen(this.labelInput_.getElement(),
                             goog.events.EventType.KEYUP,
                             this.handleKeyUp_);
};
mirosubs.subtitle.TranscribeEntry.prototype.focus = function() {
    if (this.labelInput_.getValue() == '')
        this.labelInput_.focusAndSelect();
    else
        this.labelInput_.getElement().focus();
};
mirosubs.subtitle.TranscribeEntry.prototype.handleKey_ = function(event) {
    console.log('handleKey_');
    if (event.keyCode == goog.events.KeyCodes.ENTER) {
        this.addNewTitle_();
        event.preventDefault();
    }
};
mirosubs.subtitle.TranscribeEntry.prototype.handleKeyUp_ = function(event) {
    console.log('keyUp');
    this.videoPlayer_.showCaptionText(this.labelInput_.getValue());
    this.issueLengthWarning_(this.insertsBreakableChar_(event.keyCode));
};
mirosubs.subtitle.TranscribeEntry.prototype.addNewTitle_ = function() {
    var value = this.labelInput_.getValue();
    this.labelInput_.setValue('');
    // FIXME: accessing private member of goog.ui.LabelInput
    this.labelInput_.label_ = '';
    this.labelInput_.focusAndSelect();
    this.dispatchEvent(new mirosubs.subtitle.TranscribeEntry.NewTitleEvent(value));
};
mirosubs.subtitle.TranscribeEntry.prototype.issueLengthWarning_ = function(breakable) {
    var MAX_CHARS = 100;
    var length = this.labelInput_.getValue().length;
    if (breakable && length > MAX_CHARS)
        this.addNewTitle_();
    else
        this.getElement().style.background = this.warningColor_(length, 25, MAX_CHARS);
};
mirosubs.subtitle.TranscribeEntry.prototype.warningColor_ = 
    function(length, firstChars, maxChars) {

    if (length < firstChars) 
        return "#ddd";

    length -= firstChars;
    var r = 15;
    var g = 16 - 16 * length / (maxChars - firstChars);
    var b = 12 - 12 * length / (maxChars - firstChars);
    return ["#", this.hex_(r), this.hex_(g), this.hex_(b)].join('');    
};
mirosubs.subtitle.TranscribeEntry.prototype.hex_ = function(num) {
    return goog.math.clamp(Math.floor(num), 0, 15).toString(16);
};

mirosubs.subtitle.TranscribeEntry.prototype.insertsBreakableChar_ = function(key) {
    // TODO: check the resulting char instead of what key was pressed
    return key==goog.events.KeyCodes.SPACE ||
    key==goog.events.KeyCodes.COMMA ||
    key==goog.events.KeyCodes.APOSTROPHE ||
    key==goog.events.KeyCodes.QUESTION_MARK ||
    key==goog.events.KeyCodes.SEMICOLON ||
    key==goog.events.KeyCodes.DASH ||
    key==goog.events.KeyCodes.NUM_MINUS ||
    key==goog.events.KeyCodes.NUM_PERIOD ||
    key==goog.events.KeyCodes.PERIOD ||
    key==goog.events.KeyCodes.SINGLE_QUOTE ||
    key==goog.events.KeyCodes.SLASH ||
    key==goog.events.KeyCodes.BACKSLASH ||
    key==goog.events.KeyCodes.CLOSE_SQUARE_BRACKET;
};
mirosubs.subtitle.TranscribeEntry.prototype.disposeInternal = function() {
    mirosubs.subtitle.TranscribeEntry.superClass_.disposeInternal.call(this);
    if (this.keyHandler_)
        this.keyHandler_.dispose();
};


mirosubs.subtitle.TranscribeEntry.NEWTITLE = 'newtitle';

mirosubs.subtitle.TranscribeEntry.NewTitleEvent = function(title) {
    this.type = mirosubs.subtitle.TranscribeEntry.NEWTITLE;
    this.title = title;
};
