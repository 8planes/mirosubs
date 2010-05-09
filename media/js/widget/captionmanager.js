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
 * @param {mirosubs.AbstractVideoPlayer} videoPlayer
 * @param {mirosubs.subtitle.EditableCaptionSet} captionSet
 */
mirosubs.CaptionManager = function(videoPlayer, captionSet) {
    goog.events.EventTarget.call(this);
    this.captions_ = captionSet.captionsWithTimes();
    /**
     * Compares two subs for ordering by start time.
     * @type {function(mirosubs.subtitle.EditableCaption, 
     *     mirosubs.subtitle.EditableCaption)}
     */
    this.captionCompare_ = function(a, b) {
        return a.getStartTime() - b.getStartTime();
    };
    this.binaryCompare_ = function(time, caption) {
	return time - caption.getStartTime();
    };
    this.videoPlayer_ = videoPlayer;
    this.eventHandler_ = new goog.events.EventHandler(this);
    this.eventHandler_.listen(
	videoPlayer,
	mirosubs.AbstractVideoPlayer.EventType.TIMEUPDATE,
	this.timeUpdate_);
    this.eventHandler_.listen(
	captionSet,
	goog.object.getValues(
	    mirosubs.subtitle.EditableCaptionSet.EventType),
	this.captionSetUpdate_);
	
    this.currentCaptionIndex_ = -1;
    this.lastCaptionDispatched_ = null;
    this.eventsDisabled_ = false;
};
goog.inherits(mirosubs.CaptionManager, goog.events.EventTarget);

mirosubs.CaptionManager.CAPTION = 'caption';

mirosubs.CaptionManager.prototype.captionSetUpdate_ = function(event) {
    var et = mirosubs.subtitle.EditableCaptionSet.EventType;
    if (event.type == et.CLEAR_ALL) {
	this.captions_ = [];
	this.dispatchCaptionEvent_(null);	
    }
    else if (event.type == et.UPDATED) {
	if (event.timesFirstAssigned) {
	    this.captions_.push(event.caption);
	    this.timeUpdate_();
	}
    }
};

mirosubs.CaptionManager.prototype.timeUpdate_ = function() {
    this.sendEventsForPlayheadTime_(
	this.videoPlayer_.getPlayheadTime());
};

mirosubs.CaptionManager.prototype.sendEventsForPlayheadTime_ = 
    function(playheadTime) 
{
    if (this.captions_.length == 0)
        return;
    if (this.currentCaptionIndex_ == -1 && 
        playheadTime < this.captions_[0].getStartTime())
        return;
    var curCaption = this.currentCaptionIndex_ > -1 ? 
        this.captions_[this.currentCaptionIndex_] : null;
    if (this.currentCaptionIndex_ > -1 && 
	curCaption.isShownAt(playheadTime))
        return;
    var nextCaption = this.currentCaptionIndex_ < this.captions_.length - 1 ? 
        this.captions_[this.currentCaptionIndex_ + 1] : null;
    if (nextCaption != null && 
	nextCaption.isShownAt(playheadTime)) {
        this.currentCaptionIndex_++;
        this.dispatchCaptionEvent_(nextCaption);
        return;
    }
    if ((nextCaption == null || playheadTime < nextCaption.getStartTime()) &&
        playheadTime >= curCaption.getStartTime()) {
        this.dispatchCaptionEvent_(null);
        return;
    }
    this.sendEventForRandomPlayheadTime_(playheadTime);
};

mirosubs.CaptionManager.prototype.sendEventForRandomPlayheadTime_ = 
    function(playheadTime) 
{
    var lastCaptionIndex = goog.array.binarySearch(this.captions_, 
        playheadTime, this.binaryCompare_);
    if (lastCaptionIndex < 0)
        lastCaptionIndex = -lastCaptionIndex - 2;
    this.currentCaptionIndex_ = lastCaptionIndex;
    if (lastCaptionIndex >= 0 && 
	this.captions_[lastCaptionIndex].isShownAt(playheadTime)) {
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
    this.dispatchEvent(new mirosubs.CaptionManager.CaptionEvent(caption));
};

mirosubs.CaptionManager.prototype.disposeInternal = function() {
    mirosubs.CaptionManager.superClass_.disposeInternal.call(this);
    this.eventHandler_.dispose();
};

mirosubs.CaptionManager.prototype.disableCaptionEvents = function(disabled) {
    this.eventsDisabled_ = disabled;
};

mirosubs.CaptionManager.CaptionEvent = function(editableCaption) {
    this.type = mirosubs.CaptionManager.CAPTION;
    this.caption = editableCaption;
};