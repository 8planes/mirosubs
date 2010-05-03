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

goog.provide('mirosubs.timeline.TimelineSub');

mirosubs.timeline.TimelineSub = function(
    subtitle, pixelsPerSecond, opt_pixelOffset) 
{
    goog.ui.Component.call(this);
    this.subtitle_ = subtitle;
    this.pixelsPerSecond_ = pixelsPerSecond;
    this.pixelOffset_ = opt_pixelOffset ? opt_pixelOffset : 0;
    this.editing_ = false;
    this.documentEventHandler_ = new goog.events.EventHandler(this);
};
goog.inherits(mirosubs.timeline.TimelineSub, goog.ui.Component);
mirosubs.timeline.TimelineSub.EventType = {
    START_EDITING : 'startediting',
    FINISH_EDITING : 'finishediting'
};
mirosubs.timeline.TimelineSub.prototype.createDom = function() {
    mirosubs.timeline.TimelineSub.superClass_.createDom.call(this);
    this.getElement().className = 'mirosubs-timeline-sub';
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var el = this.getElement();
    el.appendChild(this.textElem_ = $d('span'));
    el.appendChild(this.leftGrabber_ = 
                   $d('span', 'mirosubs-grabber mirosubs-leftGrabber', $d('strong')));
    el.appendChild(this.rightGrabber_ = 
                   $d('span', 'mirosubs-grabber mirosubs-rightGrabber', $d('strong')));
    this.updateValues();
};
mirosubs.timeline.TimelineSub.prototype.enterDocument = function() {
    mirosubs.timeline.TimelineSub.superClass_.enterDocument.call(this);
    this.getHandler().listen(
        this.getElement(), 'mouseover', this.onMouseOver_);
    this.getHandler().listen(
        this.getElement(), 'mouseout', this.onMouseOut_);
    this.getHandler().listen(
        this.leftGrabber_, 'mousedown', this.onGrabberMousedown_);
    this.getHandler().listen(
        this.rightGrabber_, 'mousedown', this.onGrabberMousedown_);
};
mirosubs.timeline.TimelineSub.prototype.onMouseOver_ = function(event) {
    this.setGrabberVisibility_(true);
};
mirosubs.timeline.TimelineSub.prototype.onMouseOut_ = function(event) {
    if (!this.editing_ && event.relatedTarget && 
        !goog.dom.contains(this.getElement(), event.relatedTarget))
        this.setGrabberVisibility_(false);
};
mirosubs.timeline.TimelineSub.prototype.onDocMouseMoveLeft_ = function(event) {
    // moving left grabber
    this.subtitle_.setStartTime(
        this.grabberMousedownTime_ + 
            (event.clientX - this.grabberMousedownClientX_) / 
            this.pixelsPerSecond_);
};
mirosubs.timeline.TimelineSub.prototype.onDocMouseMoveRight_ = function(event) {
    // moving right grabber
    this.subtitle_.setEndTime(
        this.grabberMousedownTime_ +
            (event.clientX - this.grabberMousedownClientX_) /
            this.pixelsPerSecond_);
};
mirosubs.timeline.TimelineSub.prototype.onDocMouseUp_ = function(event) {
    this.editing_ = false;
    this.documentEventHandler_.removeAll();
};
mirosubs.timeline.TimelineSub.prototype.onGrabberMousedown_ = 
    function(event) 
{
    var left = goog.dom.contains(this.leftGrabber_, event.target);
    this.editing_ = true;
    this.grabberMousedownClientX_ = event.clientX;
    this.grabberMousedownTime_ = left ? 
        this.subtitle_.getStartTime() : this.subtitle_.getEndTime();
    this.documentEventHandler_.listen(
        document, 'mousemove', 
        left ? this.onDocMouseMoveLeft_ : this.onDocMouseMoveRight_);
    this.documentEventHandler_.listen(
        document, 'mouseup', this.onDocMouseUp_);
};
mirosubs.timeline.TimelineSub.prototype.setGrabberVisibility_ = 
    function(visible) 
{
    var c = goog.dom.classes;
    var overClass = 'mirosubs-grabber-over';
    if (visible) {
        c.add(this.leftGrabber_, overClass);
        c.add(this.rightGrabber_, overClass);
    }
    else {
        c.remove(this.leftGrabber_, overClass);
        c.remove(this.rightGrabber_, overClass);
    }
};
mirosubs.timeline.TimelineSub.prototype.updateValues = function() {
    goog.dom.setTextContent(this.textElem_, this.subtitle_.getText());
    this.getElement().style.left = 
        (this.subtitle_.getStartTime() * 
         this.pixelsPerSecond_ - 
         this.pixelOffset_) + 'px';
    this.getElement().style.width =
        ((this.subtitle_.getEndTime() - this.subtitle_.getStartTime()) *
         this.pixelsPerSecond_) + 'px';
};
mirosubs.timeline.TimelineSub.prototype.disposeInternal = function() {
    mirosubs.timeline.TimelineSub.superClass_.disposeInternal.call(this);
    this.documentEventHandler_.dispose();
};