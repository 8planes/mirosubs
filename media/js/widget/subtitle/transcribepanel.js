// Universal Subtitles, universalsubtitles.org
// 
// Copyright (C) 2010 Participatory Culture Foundation
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see 
// http://www.gnu.org/licenses/agpl-3.0.html.

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
    this.addElems_(this.getElement());
};
mirosubs.subtitle.TranscribePanel.prototype.decorateInternal = function(el) {
    mirosubs.subtitle.TranscribePanel.superClass_.decorateInternal.call(this, el);
    this.addElems_(el);
};
mirosubs.subtitle.TranscribePanel.prototype.addElems_ = function(el) {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.getElement().appendChild(this.contentElem_ = $d('div'));
    this.addChild(this.lineEntry_ = new mirosubs.subtitle.TranscribeEntry(
        this.videoPlayer_), true);
    this.addChild(this.subtitleList_ = new mirosubs.subtitle.SubtitleList(
        this.videoPlayer_, this.captions_, false), true);
};
mirosubs.subtitle.TranscribePanel.prototype.registerRightPanel = 
    function(rightPanel) 
{
    this.getHandler().listen(rightPanel,
                             mirosubs.RightPanel.EventType.RESTART,
                             this.startOverClicked);
};
mirosubs.subtitle.TranscribePanel.prototype.createRightPanel = 
    function(serverModel) 
{
    var helpContents = new mirosubs.RightPanel.HelpContents(
        "STEP 1: Typing the subtitles",
        [["Thanks for making subtitles!! It's easy to learn ", 
          "and actually fun to do."].join(''),
         ["While you watch the video, type everything people say. Don't let ", 
          "the subtitles get too long -- hit enter for a new line."].join(''),
         ["Make sure to use the key controls below to pause and jump back, ", 
          "which will help you keep up."]],
        "Watch a quick how-to video",
        "http://youtube.com");
    var KC = goog.events.KeyCodes;
    var keySpecs = [
        new mirosubs.RightPanel.KeySpec(
            'mirosubs-play', 'mirosubs-tab', 'tab', 'Play/Pause', KC.TAB),
        new mirosubs.RightPanel.KeySpec(
            'mirosubs-skip', 'mirosubs-control', 'control', 
            'Skip Back 8 Seconds', KC.CTRL)
    ];
    return new mirosubs.RightPanel(
        serverModel, helpContents, keySpecs, true, "Done?", 
        "Next Step: Syncing");
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
/**
 *
 * @param {boolean} mode True to turn repeat on, false to turn it off.
 */
mirosubs.subtitle.TranscribePanel.prototype.setRepeatVideoMode = function(mode) {
    this.lineEntry_.setRepeatVideoMode(mode);
};

mirosubs.subtitle.TranscribePanel.prototype.startOverClicked = function() {
    var answer = confirm("Are you sure you want to start over? " +
                         "All subtitles will be deleted.");
    if (answer) {
        while (this.captions_.length > 0) {
            var caption = this.captions_.pop();
            this.unitOfWork_.registerDeleted(caption);
            // TODO: at this point, these subtitles are not in the CaptionManager.
            // But, if they are in the future (like, there is a back button in 
            // the process), then they need to be removed from the CaptionManager
            // also.
        }
        this.subtitleList_.clearAll();
        this.videoPlayer_.setPlayheadTime(0);
    }
};