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


goog.provide('mirosubs.testing.TimerStub');

/**
 * @constructor
 */
mirosubs.testing.TimerStub = function(interval) {
    goog.events.EventTarget.call(this);
    this.interval = interval;
    this.started = null;
    mirosubs.testing.TimerStub.timers.push(this);
};
goog.inherits(mirosubs.testing.TimerStub, goog.events.EventTarget);

mirosubs.testing.TimerStub.timers = [];

mirosubs.testing.TimerStub.prototype.start = function() {
    this.started = true;
};

mirosubs.testing.TimerStub.prototype.stop = function() {
    this.started = false;
};

mirosubs.testing.TimerStub.prototype.fireNow = function() {
    this.dispatchEvent(goog.Timer.TICK);
};

mirosubs.testing.TimerStub.TICK = 'tick';