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

goog.provide('mirosubs.timeline.TimeRowUL');

/**
 *
 * @param {number} spacing Spacing between major ticks, in seconds.
 */
mirosubs.timeline.TimeRowUL = function($d, spacing) {
    this.element_ = $d('ul', 'mirosubs-timeline-time');
    this.spacing_ = spacing;
    this.majorTicks_ = [];
    var i;
    for (i = 0; i < mirosubs.timeline.TimeRowUL.NUM_MAJOR_TICKS_; i++) {
        var tick = $d('li');
        this.element_.appendChild(tick);
        this.majorTicks_.push(tick);
    }
};
mirosubs.timeline.TimeRowUL.NUM_MAJOR_TICKS_ = 7;
mirosubs.timeline.TimeRowUL.prototype.getElement = function() {
    return this.element_;
};
mirosubs.timeline.TimeRowUL.prototype.setFirstTime = function(time) {
    this.firstTime_ = time;
    var i;
    for (i = 0; i < mirosubs.timeline.TimeRowUL.NUM_MAJOR_TICKS_; i++)
        goog.dom.setTextContent(
            this.majorTicks_[i], 
            mirosubs.formatTime(this.firstTime_ + i * this.spacing_));
};
mirosubs.timeline.TimeRowUL.prototype.getFirstTime = function() {
    return this.firstTime_;
};
