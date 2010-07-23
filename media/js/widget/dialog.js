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
    this.setBackgroundElementOpacity(0.8);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this.controlledVideoPlayer_ = videoSource.createControlledPlayer();
    this.videoPlayer_ = this.controlledVideoPlayer_.getPlayer();
    this.timelinePanel_ = null;
    this.captioningArea_ = null;
    this.rightPanelContainer_ = null;
    this.rightPanel_ = null;
    this.bottomPanelContainer_ = null;
};
goog.inherits(mirosubs.Dialog, goog.ui.Dialog);
mirosubs.Dialog.prototype.createDom = function() {
    mirosubs.Dialog.superClass_.createDom.call(this);
    var leftColumn = new goog.ui.Component();
    leftColumn.addChild(this.controlledVideoPlayer_, true);
    leftColumn.getElement().className = 'mirosubs-left';
    leftColumn.addChild(this.timelinePanel_ = new goog.ui.Component(), true);
    leftColumn.addChild(this.captioningArea_ = new goog.ui.Component(), true);
    this.captioningArea_.getElement().className = 'mirosubs-captioningArea';
    this.addChild(leftColumn, true);
    this.addChild(
        this.rightPanelContainer_ = new goog.ui.Component(), true);
    this.rightPanelContainer_.getElement().className = 'mirosubs-right';
    this.getContentElement().appendChild(this.getDomHelper().createDom(
        'div', 'mirosubs-clear'));
    this.addChild(
        this.bottomPanelContainer_ = new goog.ui.Component(), true);
};
/**
 * Used to display a temporary overlay, for example the instructional
 * video panel in between subtitling steps.
 * @protected
 * @param {goog.ui.Component} panel Something with absolute positioning
 *
 */
mirosubs.Dialog.prototype.showTemporaryPanel = function(panel) {
    this.hideTemporaryPanel();
    this.temporaryPanel_ = panel;
    this.addChild(panel, true);
};
/**
 * Hides and disposes the panel displayed in showTemporaryPanel.
 * @protected
 */
mirosubs.Dialog.prototype.hideTemporaryPanel = function() {
    if (this.temporaryPanel_) {
        this.temporaryPanel_.stopVideo();
        this.removeChild(this.temporaryPanel_, true);
        this.temporaryPanel_.dispose();
        this.temporaryPanel_ = null;
    }
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
mirosubs.Dialog.prototype.setVisible = function(visible) {
    mirosubs.Dialog.superClass_.setVisible.call(this, visible);
    if (!visible && mirosubs.returnURL != null) {
        goog.Timer.callOnce(function() {
            window.location.replace(mirosubs.returnURL);
        });
    }
};
mirosubs.Dialog.prototype.disposeInternal = function() {
    mirosubs.Dialog.superClass_.disposeInternal.call(this);
    this.videoPlayer_.dispose();
};