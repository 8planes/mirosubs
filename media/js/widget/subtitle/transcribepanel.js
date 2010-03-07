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
    this.addChild(this.lineEntry_ = new mirosubs.subtitle.TranscribeEntry(
                  this.videoPlayer_), true);
};

mirosubs.subtitle.TranscribePanel.prototype.enterDocument = function() {
    mirosubs.subtitle.TranscribePanel.superClass_.enterDocument.call(this);
    this.getHandler().listen(this.lineEntry_,
                             mirosubs.subtitle.TranscribeEntry.NEWTITLE,
                             this.newTitle_);
    this.getHandler().listen(this.videoPlayer_,
                             mirosubs.AbstractVideoPlayer.EventType.PLAY,
                             this.videoPlaying_);    
};

mirosubs.subtitle.TranscribePanel.prototype.videoPlaying_ = function(event) {
    this.lineEntry_.focus();
};

mirosubs.subtitle.TranscribePanel.prototype.newTitle_ = function(event) {
    var newEditableCaption = 
        new mirosubs.subtitle.EditableCaption(this.unitOfWork_);
    this.captions_.push(newEditableCaption);
    newEditableCaption.setText(event.title);
    this.subtitleList_.addSubtitle(newEditableCaption, true);
};
