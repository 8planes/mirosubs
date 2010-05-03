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

goog.provide('mirosubs.timeline.TimelineSubs');

mirosubs.timeline.TimelineSubs = function(captionSet, pixelsPerSecond) {
    goog.ui.Component.call(this);
    this.captionSet_ = captionSet;
    this.pixelsPerSecond_ = pixelsPerSecond;
    /**
     * Map of caption id to TimelineSub
     */
    this.subs_ = {};
};
goog.inherits(mirosubs.timeline.TimelineSubs, goog.ui.Component);
mirosubs.timeline.TimelineSubs.prototype.createDom = function() {
    mirosubs.timeline.TimelineSubs.superClass_.createDom.call(this);
    this.getElement().className = 'mirosubs-timeline-subs';
    var subsWithTimes = this.captionSet_.captionsWithTimes();
    var i;
    for (i = 0; i < subsWithTimes.length; i++)
        this.addSub_(subsWithTimes[i]);
};
mirosubs.timeline.TimelineSubs.prototype.enterDocument = function() {
    mirosubs.timeline.TimelineSubs.superClass_.enterDocument.call(this);
    this.getHandler().listen(
        this.captionSet_, 
        goog.object.getValues(mirosubs.subtitle.EditableCaptionSet.EventType),
        this.captionSetListener_);
};
mirosubs.timeline.TimelineSubs.prototype.captionSetListener_ = function(event) {
    var et = mirosubs.subtitle.EditableCaptionSet.EventType;
    if (event.type == et.CLEAR_ALL) {
        
    }
    else if (event.type == et.UPDATED) {
        var updatedSub = event.caption;
        if (event.timesFirstAssigned)
            this.addSub_(updatedSub);
        else
            this.subs_[updatedSub.getCaptionID() + ''].updateValues();
    }
};
mirosubs.timeline.TimelineSubs.prototype.addSub_ = function(sub) {
    var timelineSub = new mirosubs.timeline.TimelineSub(
        sub, this.pixelsPerSecond_, 0);
    this.addChild(timelineSub, true);
    this.subs_[sub.getCaptionID() + ''] = timelineSub;
};