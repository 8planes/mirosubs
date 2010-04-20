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

goog.provide('mirosubs.Dialog');

mirosubs.Dialog = function(videoSource) {
    goog.ui.Dialog.call(this, 'mirosubs-modal-widget', true);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this.videoSource_ = videoSource;
    this.videoPlayer_ = null;
    this.timelinePanel_ = null;
    this.captioningArea_ = null;
    this.rightPanelContainer_ = null;
    this.rightPanel_ = null;
};
goog.inherits(mirosubs.Dialog, goog.ui.Dialog);
mirosubs.Dialog.prototype.createDom = function() {
    mirosubs.Dialog.superClass_.createDom.call(this);
    var leftColumn = new goog.ui.Component();
    leftColumn.addChild(
        this.videoPlayer_ = this.videoSource_.createPlayer(), true);
    leftColumn.getElement().className = 'mirosubs-left';
    leftColumn.addChild(this.timelinePanel_ = new goog.ui.Component(), true);
    leftColumn.addChild(this.captioningArea_ = new goog.ui.Component(), true);
    this.captioningArea_.getElement().className = 'mirosubs-captioningArea';
    this.addChild(leftColumn, true);
    this.addChild(this.rightPanelContainer_ = new goog.ui.Component(), true);
    this.rightPanelContainer_.getElement().className = 'mirosubs-right';
    this.getContentElement().appendChild(this.getDomHelper().createDom(
        'div', 'mirosubs-clear'));
};
mirosubs.Dialog.prototype.getVideoPlayerInternal = function() {
    return this.videoPlayer_;
};
mirosubs.Dialog.prototype.getTimelinePanelInternal = function() {
    return this.timelinePanel_;
};
mirosubs.Dialog.prototype.getCaptioningAreaInternal = function() {
    return this.captioningArea_;
};
mirosubs.Dialog.prototype.setRightPanelInternal = function(rightPanel) {
    this.rightPanel_ = rightPanel;
    this.rightPanelContainer_.removeChildren(true);
    this.rightPanelContainer_.addChild(rightPanel, true);
};
mirosubs.Dialog.prototype.getRightPanelInternal = function() {
    return this.rightPanel_;
};
mirosubs.Dialog.prototype.updateLoginState = function() {
    this.rightPanel_.updateLoginState();
};
mirosubs.Dialog.prototype.disposeInternal = function() {
    mirosubs.Dialog.superClass_.disposeInternal.call(this);
    this.videoPlayer_.dispose();
};