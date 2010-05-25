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

goog.provide('mirosubs.timeline.TimeRow');

mirosubs.timeline.TimeRow = function(spacing) {
    goog.ui.Component.call(this);
    this.spacing_ = spacing;
    this.secondsPerUL_ = spacing * mirosubs.timeline.TimeRowUL.NUM_MAJOR_TICKS;
    this.pixelsPerUL_ = mirosubs.timeline.TimeRowUL.NUM_MAJOR_TICKS *
        mirosubs.timeline.TimeRowUL.PX_PER_TICK;
    this.uls_ = [];
};
goog.inherits(mirosubs.timeline.TimeRow, goog.ui.Component);
mirosubs.timeline.TimeRow.prototype.createDom = function() {
    mirosubs.timeline.TimeRow.superClass_.createDom.call(this);
    this.getElement().className = 'mirosubs-timerow';
    this.ensureVisible(0);
};
mirosubs.timeline.TimeRow.prototype.ensureVisible = function(time) {
    // always reaching 20 seconds into the future.
    var $d = 
        goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    while (this.uls_.length * this.secondsPerUL_ < time + 20) {
        var row = new mirosubs.timeline.TimeRowUL(
            this.spacing_, 
            this.uls_.length * this.secondsPerUL_);
        this.addChild(row, true);
        this.uls_.push(row);
    }
};