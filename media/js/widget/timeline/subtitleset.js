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

goog.provide('mirosubs.timeline.SubtitleSet');

mirosubs.timeline.SubtitleSet = function(editableCaptionSet, videoPlayer) {
    goog.events.EventTarget.call(this);
    this.eventHandler_ = new goog.events.EventHandler(this);
    this.editableCaptionSet_ = editableCaptionSet;
    this.videoPlayer_ = videoPlayer;
    this.createSubsToDisplay_();
    this.eventHandler_.
        listen(
            this.editableCaptionSet_,
            mirosubs.subtitle.EditableCaption.CHANGE,
            this.captionChange_).
        listen(
            this.editableCaptionSet_,
            mirosubs.subtitle.EditableCaptionSet.CLEAR_TIMES,
            this.timesCleared_);
};
goog.inherits(mirosubs.timeline.SubtitleSet, goog.events.EventTarget);

mirosubs.timeline.SubtitleSet.DISPLAY_NEW = 'displaynew';
mirosubs.timeline.SubtitleSet.CLEAR_TIMES = 'cleartimes';

mirosubs.timeline.SubtitleSet.prototype.getSubsToDisplay = function() {
    return this.subsToDisplay_;
};

mirosubs.timeline.SubtitleSet.prototype.createSubsToDisplay_ = function() {
    if (this.subsToDisplay_)
        this.disposeSubsToDisplay_();
    var that = this;
    this.subsToDisplay_ = goog.array.map(
        this.editableCaptionSet_.timelineCaptions(),
        function(c) {
            return new mirosubs.timeline.Subtitle(
                c, that.videoPlayer_);
        });
    var i;
    for (i = 0; i < this.subsToDisplay_.length - 1; i++)
        this.subsToDisplay_[i].setNextSubtitle(
            this.subsToDisplay_[i + 1]);    
};

mirosubs.timeline.SubtitleSet.prototype.timesCleared_ = function(e) {
    this.createSubsToDisplay_();
    this.dispatchEvent(mirosubs.timeline.SubtitleSet.CLEAR_TIMES);
};

mirosubs.timeline.SubtitleSet.prototype.captionChange_ = function(e) {
    if (e.timesFirstAssigned && e.target.getNextCaption() != null) {
        var newSub = new mirosubs.timeline.Subtitle(
            e.target.getNextCaption(), this.videoPlayer_);
        var lastSub = null;
        if (this.subsToDisplay_.length > 0)
            lastSub = this.subsToDisplay_[this.subsToDisplay_.length - 1];
        this.subsToDisplay_.push(newSub);
        if (lastSub != null)
            lastSub.setNextSubtitle(newSub);
        this.dispatchEvent(
            new mirosubs.timeline.SubtitleSet.DisplayNewEvent(newSub));
    }
};

mirosubs.timeline.SubtitleSet.prototype.disposeSubsToDisplay_ = function() {
    goog.array.forEach(this.subsToDisplay_, function(s) { s.dispose(); });    
};

mirosubs.timeline.SubtitleSet.prototype.disposeInternal = function() {
    mirosubs.timeline.SubtitleSet.superClass_.disposeInternal.call(this);
    this.eventHandler_.dispose();
    this.disposeSubsToDisplay_();
};

mirosubs.timeline.SubtitleSet.DisplayNewEvent = function(subtitle) {
    this.type = mirosubs.timeline.SubtitleSet.DISPLAY_NEW;
    this.subtitle = subtitle;
};