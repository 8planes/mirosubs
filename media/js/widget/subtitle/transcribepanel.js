goog.provide('mirosubs.subtitle.TranscribePanel');

/**
 * @param {Array.<mirosubs.subtitle.EditableCaption>} captions
 * @param {mirosubs.UnitOfWork} unitOfWork Used to track any new captions added 
 *     while this widget is active.
 * @param {mirosubs.VideoPlayer} videoPlayer Used to update subtitle 
 * preview on top of the video
 */
mirosubs.subtitle.TranscribePanel = function(captions, unitOfWork, videoPlayer) {
    goog.ui.Component.call(this);

    this.captions_ = captions;
    this.unitOfWork_ = unitOfWork;
    this.videoPlayer_ = videoPlayer;

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
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.getElement().appendChild(this.contentElem_ = $d('div'));
    var helpLines = [['While you watch the video, type everything people ',
                      'say in the box below. Don\'t let subtitles get too ',
                      'long-- hit enter for a new line.'].join(''), 
                     ['Make sure to use the key controls (on the left side) ',
                      'to pause and jump back, so you can keep up.'].join(''),
                     'To begin, press TAB to play and start typing.'];
    this.addChild(this.subtitleList_ = new mirosubs.subtitle.SubtitleList(
       this.captions_, false, 
       mirosubs.subtitle.SubtitleList.createHelpLi($d, helpLines, 
                                                   'Transcribing Controls', 
                                                   false, 
                                                   'PRESS TAB TO BEGIN')), 
                  true);
    this.addChild(this.lineEntry_ = new mirosubs.subtitle.TranscribeEntry(), 
                  true);
};

mirosubs.subtitle.TranscribePanel.prototype.enterDocument = function() {
    mirosubs.subtitle.TranscribePanel.superClass_.enterDocument.call(this);
    this.keyHandler_ = new goog.events.KeyHandler(this.lineEntry_.getElement());
    this.getHandler().listen(this.keyHandler_,
                             goog.events.KeyHandler.EventType.KEY,
                             this.handleLineEntryKeyDown_, false, this);
    this.getHandler().listen(document,
                             goog.events.EventType.KEYUP,
                             this.handleKeyUp_, false, this);
};

mirosubs.subtitle.TranscribePanel.prototype.addNewTitle = function() {
        var newEditableCaption = 
           new mirosubs.subtitle.EditableCaption(this.unitOfWork_);
        this.captions_.push(newEditableCaption);
        newEditableCaption.setText(this.lineEntry_.getValue());
        this.subtitleList_.addSubtitle(newEditableCaption, true);
        this.lineEntry_.clearAndFocus();
};

mirosubs.subtitle.TranscribePanel.prototype.tooLongLineWarning = function(input, breakable) {
    var hex = function(i){
        return goog.math.clamp(Math.floor(i), 0, 15).toString(16);
    }

    var warning_color = function(len, first_chars, max_chars){
      if (len<first_chars) return "#ddd"

      len-=first_chars;
      r=15;
      g = 16 - 16*len/(max_chars-first_chars);
      b = 12 - 12*len/(max_chars-first_chars);
      return "#" + hex(r) + hex(g) + hex(b);
    }

    var MAX_CHARS = 100;
    var len = input.getValue().length;
    if (breakable && len > MAX_CHARS)
        this.addNewTitle();
    else
        input.getElement().style.background = warning_color(len, 25, MAX_CHARS);
};

mirosubs.subtitle.TranscribePanel.prototype.handleLineEntryKeyDown_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.ENTER) {
        this.addNewTitle();
        event.preventDefault();
    }
};

mirosubs.subtitle.TranscribePanel.prototype.handleKeyUp_ = function(event) {
//TODO: check the resulting char instead of what key was pressed
    var insertsBreakableChar = function(key){
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

    /*live update subtitle display on video*/
    this.videoPlayer_.showCaptionText(this.lineEntry_.getValue());

    /*warn user when the inserted subtitle line it getting too long*/
    this.tooLongLineWarning(this.lineEntry_, insertsBreakableChar(event.keyCode));
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
