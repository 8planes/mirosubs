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

goog.provide('mirosubs.widget.DropLockDialog');

/**
 * @constructor
 */
mirosubs.widget.DropLockDialog = function(serverModel, jsonSubs) {
    goog.ui.Dialog.call(this, 'mirosubs-modal-lang', true);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this.didLoseSession_ = false;
    this.serverModel_ = serverModel;
    this.jsonSubs_ = jsonSubs;
    this.sessionReallyIdleTimer_ = new goog.Timer(1000);
    this.sessionReallyIdleTimer_.start();
    this.secondsIdle_ = 0;
};

goog.inherits(mirosubs.widget.DropLockDialog, goog.ui.Dialog);

mirosubs.widget.DropLockDialog.prototype.didLoseSession = function() {
    return this.didLoseSession_;
};

mirosubs.widget.DropLockDialog.prototype.createDom = function() {
    mirosubs.widget.DropLockDialog.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, 
                       this.getDomHelper());
    this.timeRemainingSpan_ = $d(
        "span", "remaining-seconds", 
        mirosubs.Dialog.SECONDS_TILL_FREEZE + "");
    this.contentDiv_ = $d('div', null);

    this.backToEditingButton_ = mirosubs.createLinkButton(
        $d, 'Nope! Get me back to subtitling', 
        "mirosubs-green-button mirosubs-big");
    this.downloadWorkLink_ = mirosubs.createLinkButton(
        $d, "download your subtitles", "inline-download-subs");
    this.tryToResumeButton_ = mirosubs.createLinkButton(
        $d, "Try to Resume Work", "mirosubs-green-button mirosubs-big");

    goog.dom.append(
        this.getContentElement(), 
        $d('h3', null, 'Warning: Idle'),
        this.contentDiv_);
    this.clearDiv_ = $d('div');
    mirosubs.style.setProperty(
        this.clearDiv_, 'clear', 'both');
    this.clearDiv_.innerHTML = "&nbsp;";
    goog.dom.append(
        this.contentDiv_,
        $d("p", null,
           "Warning: you've been idle for more than " + 
           mirosubs.Dialog.MINUTES_TILL_WARNING + 
           " minutes.  To give other users a chance to help, " + 
           "we will close your session in ",
           this.timeRemainingSpan_,
           " seconds."),
        this.backToEditingButton_,
        this.clearDiv_);
};

mirosubs.widget.DropLockDialog.prototype.showLockDroppedDom_ = function(e){
    var $d = goog.bind(this.getDomHelper().createDom, 
                       this.getDomHelper()); 
    goog.dom.removeChildren(this.contentDiv_);
    goog.dom.append(
        this.contentDiv_,
        $d("p", null,
           "We've closed your subtitling session so that other users can work on this video."),
        $d("p", null,
           "If there was work you didn't want to lose, you can ",
           this.downloadWorkLink_, 
           "."),
        this.tryToResumeButton_,
        this.clearDiv_);
};

mirosubs.widget.DropLockDialog.prototype.enterDocument = function() {
    mirosubs.widget.DropLockDialog.superClass_.enterDocument.call(this);
    this.getHandler().
        listen(
            this.backToEditingButton_,
            goog.events.EventType.CLICK,
            this.backToEditing_).
        listen(
            this.downloadWorkLink_,
            goog.events.EventType.CLICK,
            this.downloadWork_).
        listen(
            this.tryToResumeButton_,
            goog.events.EventType.CLICK,
            this.tryToResume_).
        listen(
            this.sessionReallyIdleTimer_,
            goog.Timer.TICK,
            this.timerTick_);
};

mirosubs.widget.DropLockDialog.prototype.timerTick_ = function(e) {
    this.secondsIdle_++;
    if (this.secondsIdle_ >= mirosubs.Dialog.SECONDS_TILL_FREEZE) {
        this.sessionReallyIdleTimer_.stop();
        // oh snap, shit just got real
        this.didLoseSession_ = true;
        this.serverModel_.stopTimer();
        mirosubs.Rpc.call(
            "release_lock",
            { 'draft_pk': this.serverModel_.getDraftPK() });
        this.showLockDroppedDom_();
    }
    else {
        goog.dom.setTextContent(
            this.timeRemainingSpan_,
            (mirosubs.Dialog.SECONDS_TILL_FREEZE - 
             this.secondsIdle_) + '');
    }
};

mirosubs.widget.DropLockDialog.prototype.backToEditing_ = function(e) {
    e.preventDefault();
    this.setVisible(false);
};

mirosubs.widget.DropLockDialog.prototype.downloadWork_ = function(e) {
    e.preventDefault();
    mirosubs.finishfaildialog.CopyDialog.showForSubs(this.jsonSubs_);
};

mirosubs.widget.DropLockDialog.prototype.tryToResume_ = function(e) {
    e.preventDefault();
    var that = this;
    mirosubs.Rpc.call(
        'regain_lock',
        { 'draft_pk': this.serverModel_.getDraftPK() },
        function(result) {
            if (result['response'] == 'ok') {
                alert("You have successfully resumed editing.");
                that.serverModel_.startTimer();
                that.didLoseSession_ = false;
                that.setVisible(false);
            }
            else {
                that.didLoseSession_ = true;
                alert("Sorry, someone else has started subtitling.");
            }
        },
        function() {
            alert("We had a hard time contacting the server. Are you sure you're connected?");
        });
};

mirosubs.widget.DropLockDialog.prototype.disposeInternal = function() {
    mirosubs.widget.DropLockDialog.superClass_.disposeInternal.call(this);
    this.sessionReallyIdleTimer_.dispose();
};
