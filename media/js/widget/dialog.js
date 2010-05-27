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
    this.controlledVideoPlayer_ = videoSource.createControlledPlayer();
    this.videoPlayer_ = this.controlledVideoPlayer_.getPlayer();
    this.timelinePanel_ = null;
    this.captioningArea_ = null;
    this.rightPanelContainer_ = null;
    this.rightPanel_ = null;
    this.bottomPanelContainer_ = null;
};
goog.inherits(mirosubs.Dialog, goog.ui.Dialog);
mirosubs.Dialog.ComponentType = {
    MAIN : 'main',
    ALT : 'alt'
};
mirosubs.Dialog.prototype.createDom = function() {
    mirosubs.Dialog.superClass_.createDom.call(this);

    this.mainComponent_ = new goog.ui.Component();
    this.altComponent_ = new goog.ui.Component();

    var leftColumn = new goog.ui.Component();
    leftColumn.addChild(this.controlledVideoPlayer_, true);
    leftColumn.getElement().className = 'mirosubs-left';
    leftColumn.addChild(this.timelinePanel_ = new goog.ui.Component(), true);
    leftColumn.addChild(this.captioningArea_ = new goog.ui.Component(), true);
    this.captioningArea_.getElement().className = 'mirosubs-captioningArea';
    this.mainComponent_.addChild(leftColumn, true);
    this.mainComponent_.addChild(
        this.rightPanelContainer_ = new goog.ui.Component(), true);
    this.rightPanelContainer_.getElement().className = 'mirosubs-right';
    this.getContentElement().appendChild(this.getDomHelper().createDom(
        'div', 'mirosubs-clear'));
    this.mainComponent_.addChild(
        this.bottomPanelContainer_ = new goog.ui.Component(), true);
    this.addChild(this.mainComponent_, true);
    this.componentType_ = mirosubs.Dialog.ComponentType.MAIN;
};
mirosubs.Dialog.prototype.getAltComponentInternal = function() {
    return this.altComponent_;
};
/**
 * @protected
 * @param {mirosubs.Dialog.ComponentType} componentType
 */
mirosubs.Dialog.prototype.setComponentInternal = function(componentType) {
    if (componentType == this.componentType_)
        return;
    this.removeChildren(true);
    this.videoPlayer_.pause();
    var ct = mirosubs.Dialog.ComponentType;
    if (componentType == ct.MAIN)
        this.addChild(this.mainComponent_, true);
    else if (componentType == ct.ALT)
        this.addChild(this.altComponent_, true);
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
mirosubs.Dialog.prototype.getBottomPanelContainerInternal = function() {
    return this.bottomPanelContainer_;
};
mirosubs.Dialog.prototype.updateLoginState = function() {
    this.rightPanel_.updateLoginState();
};
mirosubs.Dialog.prototype.disposeInternal = function() {
    mirosubs.Dialog.superClass_.disposeInternal.call(this);
    this.videoPlayer_.dispose();
};