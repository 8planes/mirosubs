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

/**
 * @fileoverview A model in true MVC sense: dispatches events when model 
 *     changes. This keeps disparate parts of the UI which are interested 
 *     in model state (e.g. timeline, sync panel, video) informed when 
 *     alterations are made to subtitles.
 */

goog.provide('mirosubs.subtitle.EditableCaptionSet');

mirosubs.subtitle.EditableCaptionSet = function(unitOfWork, existingJsonCaptions) {
    goog.events.EventTarget.call(this);
    this.unitOfWork_ = unitOfWork;
    this.updateFn_ = goog.bind(this.captionUpdated_, this);
    var updateFn = this.updateFn_;
    this.captions_ = goog.array.map(
        existingJsonCaptions, function(caption) { 
            return new mirosubs.subtitle.EditableCaption(updateFn, caption);
        });
    var i;
    for (i = 1; i < this.captions_.length; i++) {
        this.captions_[i - 1].setNextCaption(this.captions_[i]);
        this.captions_[i].setPreviousCaption(this.captions_[i - 1]);
    }
};
goog.inherits(mirosubs.subtitle.EditableCaptionSet, goog.events.EventTarget);
mirosubs.subtitle.EditableCaptionSet.EventType = {
    CLEAR_ALL : 'clearall',
    UPDATED : 'updated'
};
mirosubs.subtitle.EditableCaptionSet.prototype.captionsWithTimes =
    function() 
{
    return goog.array.filter(
        this.captions_, function(c) { return c.getStartTime() != -1; });
};
mirosubs.subtitle.EditableCaptionSet.prototype.clear = function() {
    var caption;
    while (this.captions_.length > 0) {
        caption = this.captions_.pop();
        this.unitOfWork_.registerDeleted(caption);
    }
    this.dispatchEvent(
        mirosubs.subtitle.EditableCaptionSet.EventType.CLEAR_ALL);
};
mirosubs.subtitle.EditableCaptionSet.prototype.clearTimes = function() {
    goog.array.forEach(this.captions_, function(c) { c.clearTimes(); });
};
mirosubs.subtitle.EditableCaptionSet.prototype.count = function() {
    return this.captions_.length;
};
mirosubs.subtitle.EditableCaptionSet.prototype.caption = function(index) {
    return this.captions_[index];
};
mirosubs.subtitle.EditableCaptionSet.prototype.addNewCaption = function() {
    var c = new mirosubs.subtitle.EditableCaption(this.updateFn_);
    this.captions_.push(c);
    if (this.captions_.length > 1) {
        var previousCaption = this.captions_[this.captions_.length - 2];
        previousCaption.setNextCaption(c);
        c.setPreviousCaption(previousCaption);
    }
    this.unitOfWork_.registerNew(c);
    return c;
};
/**
 * Find the last subtitle with a start time at or before time.
 * @param {number} time
 * @return {?mirosubs.subtitle.EditableCaption} null if before first 
 *     sub start time, or last subtitle with start time 
 *     at or before playheadTime.
 */
mirosubs.subtitle.EditableCaptionSet.prototype.findLastForTime = 
    function(time) 
{
    var i;
    // TODO: write unit test then get rid of linear search in future.
    for (i = 0; i < this.captions_.length; i++)
        if (this.captions_[i].getStartTime() != -1 &&
            this.captions_[i].getStartTime() <= time &&
            (i == this.captions_.length - 1 ||
             this.captions_[i + 1].getStartTime() == -1 ||
             this.captions_[i + 1].getStartTime() > time))
            return this.captions_[i];
    return null;
};
mirosubs.subtitle.EditableCaptionSet.prototype.captionUpdated_ = 
    function(caption, timesFirstAssigned) 
{
    this.unitOfWork_.registerUpdated(caption);
    this.dispatchEvent(
        new mirosubs.subtitle.EditableCaptionSet.UpdateEvent(
            caption, timesFirstAssigned));
};
mirosubs.subtitle.EditableCaptionSet.UpdateEvent = 
    function(caption, timesFirstAssigned) 
{
    this.type = mirosubs.subtitle.EditableCaptionSet.EventType.UPDATED;
    this.caption = caption;
    this.timesFirstAssigned = timesFirstAssigned;
};