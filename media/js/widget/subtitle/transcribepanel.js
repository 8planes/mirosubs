goog.provide('mirosubs.subtitle.TranscribePanel');

/**
 * @param {Array.<mirosubs.subtitle.EditableCaption>} captions
 * @param {mirosubs.UnitOfWork} unitOfWork Used to track any new captions added 
 *     while this widget is active.
 */
mirosubs.subtitle.TranscribePanel = function(captions, unitOfWork) {
    goog.ui.Component.call(this);

    this.captions_ = captions;
    this.unitOfWork_ = unitOfWork;


    /**
     * @type {?goog.events.KeyHandler}
     * @private
     */
    this.keyHandler_ = null;
};
goog.inherits(mirosubs.subtitle.TranscribePanel, goog.ui.Component);

mirosubs.subtitle.TranscribePanel.prototype.getContentElement = function() {
    return this.contentElem_;
};

mirosubs.subtitle.TranscribePanel.prototype.createDom = function() {
    mirosubs.subtitle.TranscribePanel.superClass_.createDom.call(this);
    var el = this.getElement();
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    el.appendChild($d('div', {'class':'mirosubs-tips'},
                      $d('p', null, ['Tap spacebar to begin, and tap again ',
                                     'to align each subtitle.'].join('')),
                      $d('p', null, 'TAB = Play/Pause  CTRL = Skip Back')));
    el.appendChild(this.contentElem_ = $d('div'));
    this.addChild(this.subtitleList_ = new mirosubs.subtitle.SubtitleList(
       this.captions_, 
       false,
       mirosubs.subtitle.Util
       .createHelpLi(this.getDomHelper(),
                     [['When people start speaking, type everything ',
                       'they say in the box below.'].join(''),
                      ['Don\'t let subtitles get too long! Hit enter ',
                       'at the end of each line.'].join('')])), true);
    this.addChild(this.lineEntry_ = new mirosubs.subtitle.TranscribeEntry(), 
                  true);
};

mirosubs.subtitle.TranscribePanel.prototype.enterDocument = function() {
    mirosubs.subtitle.TranscribePanel.superClass_.enterDocument.call(this);
    this.keyHandler_ = new goog.events.KeyHandler(this.lineEntry_.getElement());
    this.getHandler().listen(this.keyHandler_,
                             goog.events.KeyHandler.EventType.KEY,
                             this.handleLineEntryKey_, false, this);
};

mirosubs.subtitle.TranscribePanel.prototype.getCurrentCaption = function() {
    return this.lineEntry_.getValue();
};

mirosubs.subtitle.TranscribePanel.prototype.handleLineEntryKey_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.ENTER) {
        var newEditableCaption = 
           new mirosubs.subtitle.EditableCaption(this.unitOfWork_);
        this.captions_.push(newEditableCaption);
        newEditableCaption.setText(this.lineEntry_.getValue());
        this.subtitleList_.addSubtitle(newEditableCaption, true);
        this.lineEntry_.clearAndFocus();
        event.preventDefault();
    }
};

mirosubs.subtitle.TranscribeEntry = function() {
    goog.ui.Component.call(this);
};
goog.inherits(mirosubs.subtitle.TranscribeEntry, goog.ui.Component);
mirosubs.subtitle.TranscribeEntry.prototype.createDom = function() {
    mirosubs.subtitle.TranscribeEntry.superClass_.createDom.call(this);
    this.getElement().setAttribute('class', 'mirosubs-transcribeControls');
    this.addChild(this.labelInput_ = new goog.ui.LabelInput('Type subtitle'), true);
    this.labelInput_.LABEL_CLASS_NAME = 'mirosubs-label-input-label';
    goog.dom.classes.add(this.labelInput_.getElement(), 'trans');
};
mirosubs.subtitle.TranscribeEntry.prototype.getValue = function() {
    return this.labelInput_.getValue();
};
mirosubs.subtitle.TranscribeEntry.prototype.clearAndFocus = function() {
    this.labelInput_.setValue('');
    this.labelInput_.focusAndSelect();
};
