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

goog.provide('mirosubs.subtitle.TranscribeEntry');

mirosubs.subtitle.TranscribeEntry = function(videoPlayer) {
    goog.ui.Component.call(this);
    this.videoPlayer_ = videoPlayer;
    /**
     * The time at which continuous typing last started. Set to null at the 
     * beginning of a new subtitle and also after a pause of S seconds.
     * @type {?number}
     */
    this.firstKeyStrokeTime_ = null;
    this.firstKeyStrokePlayheadTime_ = null;
    this.repeatVideoMode_ = false;
    this.typingPauseTimer_ = new goog.Timer(
        mirosubs.subtitle.TranscribeEntry.S * 1000);
};
goog.inherits(mirosubs.subtitle.TranscribeEntry, goog.ui.Component);
mirosubs.subtitle.TranscribeEntry.logger_ = 
    goog.debug.Logger.getLogger('mirosubs.subtitle.TranscribeEntry');

/**
 * Number of seconds of continuous typing before restarting to 
 * firstKeyStrokePlayheadTime_ - R
 */
mirosubs.subtitle.TranscribeEntry.P = 4;
mirosubs.subtitle.TranscribeEntry.R = 6;
/**
 * Minimum number of seconds to pause before restarting typingPauseTimer_
 */
mirosubs.subtitle.TranscribeEntry.S = 1;

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
    this.getHandler().listen(this.typingPauseTimer_,
                             goog.Timer.TICK,
                             this.typingPauseTimerTick_);
    mirosubs.subtitle.TranscribeEntry.logger_.info(
        "P is set to " + mirosubs.subtitle.TranscribeEntry.P);
    mirosubs.subtitle.TranscribeEntry.logger_.info(
        "R is set to " + mirosubs.subtitle.TranscribeEntry.R);
    mirosubs.subtitle.TranscribeEntry.logger_.info(
        "S is set to " + mirosubs.subtitle.TranscribeEntry.S);
};
mirosubs.subtitle.TranscribeEntry.prototype.focus = function() {
    if (this.labelInput_.getValue() == '')
        this.labelInput_.focusAndSelect();
    else
        this.labelInput_.getElement().focus();
};
mirosubs.subtitle.TranscribeEntry.prototype.handleKey_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.ENTER) {
        event.preventDefault();
        this.addNewTitle_();
    }
    else if (event.keyCode != goog.events.KeyCodes.TAB && 
             this.repeatVideoMode_) {
        if (this.firstKeyStrokeTime_ == null) {
            var now = new Date();
            var playheadTime = this.videoPlayer_.getPlayheadTime()
            mirosubs.subtitle.TranscribeEntry.logger_.info(
                "Setting firstKeyStrokeTime_ to " + 
                    now.getTime());
            mirosubs.subtitle.TranscribeEntry.logger_.info(
                "Setting firstKeyStrokePlayheadTime_ to " + 
                    playheadTime);
            this.firstKeyStrokeTime_ = now;
            this.firstKeyStrokePlayheadTime_ = playheadTime;
            this.typingPauseTimer_.start();
        }
        else {
            // restart timer.
            this.typingPauseTimer_.stop();
            this.typingPauseTimer_.start();
        }
    }
};
mirosubs.subtitle.TranscribeEntry.prototype.typingPauseTimerTick_ = function() {
    // S seconds since last keystroke!
    var now = new Date();
    var typingTime = (now.getTime() - this.firstKeyStrokeTime_.getTime()) / 1000;
    this.firstKeyStrokeTime_ = null;
    this.typingPauseTimer_.stop();
    if (typingTime >= mirosubs.subtitle.TranscribeEntry.P) {
        mirosubs.subtitle.TranscribeEntry.logger_.info(
            ["Over P seconds of continuous typing followed by a pause of S. ",
             "Restarting video to firstKeyStrokePlayheadTime_ - R"].join(''));
        this.videoPlayer_.setPlayheadTime(
            this.firstKeyStrokePlayheadTime_ - 
                mirosubs.subtitle.TranscribeEntry.R);
    }
    else
        mirosubs.subtitle.TranscribeEntry.logger_.info(
            ["Typing followed by a pause of S, but typing was not ", 
             "continuous for over P seconds"].join(''));
};
/**
 * Turns Repeat Video Mode on or off. When this mode is turned on, the video 
 * repeats during typing. The mode is off by default.
 * @param {boolean} mode True to turn Repeat Video Mode on, false to turn it off.
 */
mirosubs.subtitle.TranscribeEntry.prototype.setRepeatVideoMode = function(mode) {
    this.repeatVideoMode_ = mode;
    this.firstKeyStrokeTime_ = null;
    this.typingPauseTimer_.stop();
};
mirosubs.subtitle.TranscribeEntry.prototype.handleKeyUp_ = function(event) {
    this.videoPlayer_.showCaptionText(this.labelInput_.getValue());
    this.issueLengthWarning_(this.insertsBreakableChar_(event.keyCode));
};
mirosubs.subtitle.TranscribeEntry.prototype.addNewTitle_ = function() {
    var value = this.labelInput_.getValue();
    // FIXME: accessing private member of goog.ui.LabelInput
    this.labelInput_.label_ = '';
    this.labelInput_.setValue('');
    this.labelInput_.focusAndSelect();
    this.firstKeyStrokeTime_ = null;
    this.typingPauseTimer_.stop();
    this.dispatchEvent(new mirosubs.subtitle.TranscribeEntry
                       .NewTitleEvent(value));
};
mirosubs.subtitle.TranscribeEntry.prototype.issueLengthWarning_ = function(breakable) {
    var MAX_CHARS = 100;
    var length = this.labelInput_.getValue().length;
    if (breakable && length > MAX_CHARS)
        this.addNewTitle_();
    else
        this.getElement().style.background = this.warningColor_(length, 50, MAX_CHARS);
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
    if (this.typingPauseTimer_) {
        this.typingPauseTimer_.dispose();
        this.typingPauseTimer_ = null;
    }
};

mirosubs.subtitle.TranscribeEntry.NEWTITLE = 'newtitle';

mirosubs.subtitle.TranscribeEntry.NewTitleEvent = function(title) {
    this.type = mirosubs.subtitle.TranscribeEntry.NEWTITLE;
    this.title = title;
};
