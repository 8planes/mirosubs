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

goog.provide('mirosubs.CaptionManager');

/**
 * Constructor.
 *
 * @param {?function(): number} playheadFn Optional function that 
 *     returns the current 
 *     playhead time of the video, in seconds.
 */
mirosubs.CaptionManager = function(playheadFn) {
    goog.events.EventTarget.call(this);
    this.captions_ = [];
    this.captionCompare_ = function(a, b) {
        return a['start_time'] > b['start_time'] ? 
            1 : a['start_time'] < b['start_time'] ? -1 : 0;
    };
    this.playheadFn_ = playheadFn;
    var that = this;
    this.timerInterval_ = window.setInterval(function() { that.timerTick_(); }, 100);
    this.currentCaptionIndex_ = -1;
    this.lastCaptionDispatched_ = null;
    this.eventsDisabled_ = false;
};
goog.inherits(mirosubs.CaptionManager, goog.events.EventTarget);

mirosubs.CaptionManager.EventType = {
    CAPTION: 'caption'
};

/**
 * Adds captions to be displayed.
 * @param {Array.<Object.<string, *>>} captions Array of captions. Each caption must be an 
 *     object with a 'start_time' property set to the start time for 
 *     that caption and an 'end_time' property set to the end time.
 */
mirosubs.CaptionManager.prototype.addCaptions = function(captions) {
    // TODO: perhaps use a more efficient implementation in the future, if 
    // that is appealing. For example, sort-merge.
    var i;
    for (i = 0; i < captions.length; i++)
        this.captions_.push(captions[i]);
    goog.array.sort(this.captions_, this.captionCompare_);
    this.currentCaptionIndex_ = -1;
    this.timerTick_();
};

mirosubs.CaptionManager.prototype.removeAll = function() {
    this.captions_ = [];
    this.dispatchCaptionEvent_(null);    
};

/**
 * 
 * @param {mirosubs.subtitle.EditableCaption.UpdateEvent} event
 */
mirosubs.CaptionManager.prototype.captionUpdated = function(event) {
    if (event.timesFirstAssigned)
        this.addCaptions([event.caption.jsonCaption]);
};

mirosubs.CaptionManager.prototype.timerTick_ = function() {
    if (this.playheadFn_ != null)
        this.sendEventsForPlayheadTime_(this.playheadFn_());
};

mirosubs.CaptionManager.prototype.sendEventsForPlayheadTime_ = function(playheadTime) {
    if (this.captions_.length == 0)
        return;
    if (this.currentCaptionIndex_ == -1 && 
        playheadTime < this.captions_[0]['start_time'])
        return;
    var curCaption = this.currentCaptionIndex_ > -1 ? 
        this.captions_[this.currentCaptionIndex_] : null;
    if (this.currentCaptionIndex_ > -1 && 
        playheadTime >= curCaption['start_time'] && 
        playheadTime < curCaption['end_time'])
        return;
    var nextCaption = this.currentCaptionIndex_ < this.captions_.length - 1 ? 
        this.captions_[this.currentCaptionIndex_ + 1] : null;
    if (nextCaption != null && 
        playheadTime >= nextCaption['start_time'] &&
        playheadTime < nextCaption['end_time']) {
        this.currentCaptionIndex_++;
        this.dispatchCaptionEvent_(nextCaption);
        return;
    }
    if ((nextCaption == null || playheadTime < nextCaption['start_time']) &&
        playheadTime >= curCaption['start_time']) {
        this.dispatchCaptionEvent_(null);
        return;
    }
    this.sendEventForRandomPlayheadTime_(playheadTime);
};

mirosubs.CaptionManager.prototype.sendEventForRandomPlayheadTime_ = function(playheadTime) {
    var lastCaptionIndex = goog.array.binarySearch(this.captions_, 
        { 'start_time' : playheadTime }, this.captionCompare_);
    if (lastCaptionIndex < 0)
        lastCaptionIndex = -lastCaptionIndex - 2;
    this.currentCaptionIndex_ = lastCaptionIndex;
    if (lastCaptionIndex >= 0 && 
        playheadTime >= this.captions_[lastCaptionIndex]['start_time'] &&
        playheadTime <= this.captions_[lastCaptionIndex]['end_time']) {
        this.dispatchCaptionEvent_(this.captions_[lastCaptionIndex]);
    }
    else {        
        this.dispatchCaptionEvent_(null);
    }
};

mirosubs.CaptionManager.prototype.dispatchCaptionEvent_ = function(caption) {
    if (caption == this.lastCaptionDispatched_)
        return;
    if (this.eventsDisabled_)
        return;
    this.lastCaptionDispatched_ = caption;
    var event = new goog.events.Event(
        mirosubs.CaptionManager.EventType.CAPTION, this);
    event.caption = caption;
    this.dispatchEvent(event);
};

mirosubs.CaptionManager.prototype.disposeInternal = function() {
    mirosubs.CaptionManager.superClass_.disposeInternal.call(this);
    window.clearInterval(this.timerInterval_);
};

mirosubs.CaptionManager.prototype.disableCaptionEvents = function(disabled) {
    this.eventsDisabled_ = disabled;
};