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

/**
 * @constructor
 *
 */
mirosubs.Dialog = function(videoSource) {
    goog.ui.Dialog.call(this, 'mirosubs-modal-widget', true);
    this.setBackgroundElementOpacity(0.8);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this.setEscapeToCancel(false);
    /**
     * This only becomes non-null on finish, when the server sends back 
     * new contents for the drop-down menu.
     * @type {mirosubs.widget.DropDownContents}
     */
    this.dropDownContents_ = null;
    this.controlledVideoPlayer_ = videoSource.createControlledPlayer();
    this.videoPlayer_ = this.controlledVideoPlayer_.getPlayer();
    this.timelinePanel_ = null;
    this.captioningArea_ = null;
    this.rightPanelContainer_ = null;
    this.rightPanel_ = null;
    this.bottomPanelContainer_ = null;
    this.idleTimer_ = new goog.Timer(60000);
    this.idleTimer_.start();
    this.minutesIdle_ = 0;
};
goog.inherits(mirosubs.Dialog, goog.ui.Dialog);

/* @const {int}
 * Number of minutes until the idle dialog is show
 */
mirosubs.Dialog.MINUTES_TILL_WARNING = 5;

/* @const {int}
 * Number of seconds after the idle dialog is show that
 * the current user session will be suspended. 
 */
mirosubs.Dialog.SECONDS_TILL_FREEZE = 120;

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
mirosubs.Dialog.prototype.enterDocument = function() {
    mirosubs.Dialog.superClass_.enterDocument.call(this);
    this.getHandler().
        listen(mirosubs.ClosingWindow.getInstance(),
               mirosubs.ClosingWindow.BEFORE_UNLOAD,
               this.onBeforeWindowUnload_).
        listen(mirosubs.ClosingWindow.getInstance(),
               mirosubs.ClosingWindow.UNLOAD,
               this.onWindowUnload_).
        listen(mirosubs.userEventTarget,
               mirosubs.EventType.LOGIN,
               this.updateLoginState).
        listen(goog.dom.getDocumentScrollElement(),
               [goog.events.EventType.KEYDOWN,
                goog.events.EventType.MOUSEMOVE], 
               this.userIsNotIdle_).
        listen(this.idleTimer_,
               goog.Timer.TICK,
               this.idleTimerTick_);
};

mirosubs.Dialog.prototype.userIsNotIdle_ = function() {
    this.minutesIdle_ = 0;
};

mirosubs.Dialog.prototype.idleTimerTick_ = function() {
    this.minutesIdle_++;
    if (this.minutesIdle_ >= mirosubs.Dialog.MINUTES_TILL_WARNING) {
        this.showIdleWarning_();
    }
};

mirosubs.Dialog.prototype.showIdleWarning_ = function() {
    this.idleTimer_.stop();
    var serverModel = this.getServerModel();
    if (!serverModel)
        return;
    var dropLockDialog = new mirosubs.widget.DropLockDialog(
        serverModel, this.makeJsonSubs());
    this.getHandler().listen(
        dropLockDialog,
        goog.ui.Dialog.EventType.AFTER_HIDE,
        this.dropLockDialogHidden_);
    dropLockDialog.setVisible(true);
};

mirosubs.Dialog.prototype.dropLockDialogHidden_ = function(e) {
    var dialog = e.target;
    if (dialog.didLoseSession())
        this.hideDialogImpl_();
    else
        this.idleTimer_.start();
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
/**
 * Returns true if there's no work, or if there has been work
 * but it was saved.
 * @protected
 */
mirosubs.Dialog.prototype.isWorkSaved = goog.abstractMethod;
/**
 * This corresponds to the finish button. It is not called during periodic saves.
 * @protected
 * @param {boolean} closeAfterSave
 */
mirosubs.Dialog.prototype.saveWork = function(closeAfterSave) {
    mirosubs.Tracker.getInstance().trackPageview('Submits_final_work_in_widget');
    if (mirosubs.IS_NULL) {
        this.saved_ = true;
        var message = "Congratulations, you have completed a demo. There is a web full of videos waiting for your translations, enjoy!";
        //This should likely have a nicer modal
        alert(message);
        this.setVisible(false);
        return;
    }
    if (mirosubs.currentUsername == null && !mirosubs.isLoginAttemptInProgress())
        mirosubs.login(function(loggedIn) {
            if (!loggedIn) {
                alert("We had a problem logging you in. You might want to check " +
                      "your web connection and try again.\n\nYou can also download " +
                      "your subtitles using the download button in the lower right corner " +
                      "of the dialog and email them to widget-logs@universalsubtitles.org.");
            }
        });
    else
        this.saveWorkInternal(closeAfterSave);
};
mirosubs.Dialog.prototype.saveWorkInternal = function(closeAfterSave) {
    goog.abstractMethod();
};
mirosubs.Dialog.prototype.onBeforeWindowUnload_ = function(event) {
    if (!this.isWorkSaved())
        event.message = "You have unsaved work.";
};
mirosubs.Dialog.prototype.onWindowUnload_ = function() {
    mirosubs.widget.ResumeEditingRecord.clear();
};
mirosubs.Dialog.prototype.setVisible = function(visible) {
    if (visible) {
        mirosubs.Dialog.superClass_.setVisible.call(this, true);
        goog.dom.getDocumentScrollElement().scrollTop = 0;
    }
    else {
        if (this.isWorkSaved()) {
            this.hideDialogImpl_();
        }
        else {
            this.showSaveWorkDialog_();
        }
    }
};
/**
 * @protected
 * @param {mirosubs.widget.DropDownContents} dropDownContents
 */
mirosubs.Dialog.prototype.setDropDownContentsInternal = function(dropDownContents) {
    this.dropDownContents_ = dropDownContents;
};
mirosubs.Dialog.prototype.getDropDownContents = function() {
    return this.dropDownContents_;
};
mirosubs.Dialog.prototype.showSaveWorkDialog_ = function() {
    var that = this;
    var unsavedWarning = new mirosubs.UnsavedWarning(function(submit) {
        if (submit)
            that.saveWork(true);
        else {
            that.hideDialogImpl_(false);
        }
    });
    unsavedWarning.setVisible(true);
};

mirosubs.Dialog.prototype.getServerModel = goog.abstractMethod;

/**
 * @protected
 */
mirosubs.Dialog.prototype.hideToFork = function() {
    // we just want to hide translation dialog to switch to subtitling dialog
    // because of a fork. so skip releasing the lock and changing the location.
    mirosubs.Dialog.superClass_.setVisible.call(this, false);
};

mirosubs.Dialog.prototype.hideDialogImpl_ = function() {
    var serverModel = this.getServerModel();
    if (serverModel){
        var args = {};
        args['session_pk'] = serverModel.getSessionPK();
        mirosubs.Rpc.call("release_lock", args);    
    }
    mirosubs.widget.ResumeEditingRecord.clear();
    if (mirosubs.returnURL != null) {
        goog.Timer.callOnce(function() {
            window.location.replace(mirosubs.returnURL);
        });
    }
    mirosubs.Dialog.superClass_.setVisible.call(this, false);
};

mirosubs.Dialog.prototype.makeJsonSubs = goog.abstractMethod;

mirosubs.Dialog.prototype.disposeInternal = function() {
    mirosubs.Dialog.superClass_.disposeInternal.call(this);
    this.videoPlayer_.dispose();
    this.idleTimer_.dispose();
};
