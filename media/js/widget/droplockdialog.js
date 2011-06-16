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

goog.provide('mirosubs.widget.droplockdialog.Dialog');

/**
 * @constructor
 * @param {string} videoID
*/
mirosubs.widget.droplockdialog.Dialog = function(secondsUntilWarning,  secondsUntilFreeze, eventNode){
    goog.ui.Dialog.call(this, 'mirosubs-modal-lang', true);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    /*
     * @type {int}
     */
    this.secondsUntilFreeze_ = secondsUntilFreeze;
    /*
     * @type {int}
     */
    this.initialSecondsUntilFreeze_ = secondsUntilFreeze;
    /*
     * @type {int}
     */
    this.secondsUntilWarning_ = secondsUntilWarning;

    this.warningTimer_ = null;
    // we reset our timer on any inactivity, 
    // mouse event or keyboard press
    this.inputHandler_ = new goog.events.InputHandler(eventNode);
    goog.events.listen(this.inputHandler_, goog.events.InputHandler.EventType.INPUT,
                   goog.bind(this.startLockoutTimer_, this));
    goog.events.listen(eventNode, "mousemove",
                   goog.bind(this.startLockoutTimer_, this));
    // create proper ENUM for this
    this.state = 'IDLE';
    this.startLockoutTimer_();   
    // TODO: dispose events
};

goog.inherits(mirosubs.widget.droplockdialog.Dialog, goog.ui.Dialog);

mirosubs.widget.droplockdialog.Dialog.prototype.reset_ = function (){
    this.startLockoutTimer_();
    this.setVisible(false);
    this.state = 'IDLE';
}

/* Starts the timer for dropping the lock on this editing session, if 
 * called multiple times will properly clear the old timer and start a new one.
 */
mirosubs.widget.droplockdialog.Dialog.prototype.startLockoutTimer_ = function (){
    if (this.idleTimer_){
        this.idleTimer_.stop();
    }else{
        // TODO: should we use a goog.ui.IdleTimer instead of our own idleTimer?
        this.idleTimer_ = new goog.Timer(this.secondsUntilWarning_ * 1000);
        goog.events.listen(this.idleTimer_, goog.Timer.TICK, 
                           goog.bind(this.showWarning_, this));
    }
    this.idleTimer_.start();
        
    
};

mirosubs.widget.droplockdialog.Dialog.prototype.createWarningDom = function() {
    // TODOS: layout issues 
    var $d = goog.bind(this.getDomHelper().createDom, 
                       this.getDomHelper());
    var el = this.getElement();
    goog.dom.removeChildren(el);
    el.appendChild(
        $d('h3', null, 'Warning, idle'));
    this.contentDiv_ = $d('div', null);
    var pText = "Warning: you've been idle for "
        + this.toMinutes(this.secondsUntilWarning_)
        + ' minutes.  To give other users a chance to help, we will close your session in ';
    this.timeRemainingSpan_ = $d( "span", "remaining-minutes");
    var p = $d( "p", null, pText, this.timeRemainingSpan_);
    
    //p.appendChild(this.timeRemainingSpan_);
    this.contentDiv_.appendChild(p);
    
    this.contentDiv_.appendChild(this.timeRemainingSpan_);
    goog.dom.append(this.contentDiv_, ".");

    el.appendChild(this.contentDiv_);
    this.backToEditingButton_ = 
        $d('a', 
           {'href':'#', 
            'className': "mirosubs-green-button mirosubs-big"}, 
           'Nope! Get me back to subtitling');
   goog.events.listen(this.backToEditingButton_, "click",
                     goog.bind(this.onBackToEditing_, this));
   el.appendChild( this.backToEditingButton_);
    this.state = 'WARNINING';
};

mirosubs.widget.droplockdialog.Dialog.prototype.createDom = function() {
    mirosubs.startdialog.Dialog.superClass_.createDom.call(this);
    this.createWarningDom();

};

mirosubs.widget.droplockdialog.Dialog.prototype.showWarning_ = function(e){
    // TODOS: layout issues 
    if (this.state != 'IDLE'){
        return;
    }
    this.idleTimer_.disposeInternal();
    this.idleTimer_ = null;
    this.warningTimer_ = new goog.Timer(1000);
    
    goog.events.listen(this.warningTimer_, goog.Timer.TICK, 
                       goog.bind(this.onUpdateTimeDisplay_, this));
    this.warningTimer_.start();
    this.setVisible(true);
    this.state_ = "WARNING";
    this.secondsUntilFreeze_ = this.initialSecondsUntilFreeze_;
    this.onUpdateTimeDisplay_();
};

mirosubs.widget.droplockdialog.Dialog.prototype.createLockDroppedDom_ = function(e){
        var $d = goog.bind(this.getDomHelper().createDom, 
                           this.getDomHelper()); 
    var el = this.getElement();
    goog.dom.removeChildren(el);
    el.appendChild(
        $d('h3', null, 'Warning, idle'));
    this.contentDiv_ = $d('div', null);
    var p = $d("p", null, "Since you were idle for " +
               this.toMinutes( this.secondsUntilWarning_) 
               + " minutes, we've closed your subtitling session so that other users can work on this video.\n\n" +
               "If there was work you don't want to lose, ");
    
    this.downloadWorkButton_ = $d("a", "inline-download-subs", "download subtitles here.");
    goog.dom.setProperties(this.downloadWorkButton_, {"href":"#"});
    goog.dom.appendChild(p, this.downloadWorkButton_);
    goog.events.listen(this.downloadWorkButton_, 'click', goog.bind(this.onDownloadWorkClicked, this));
    
    //goog.dom.setTextContent(this.backToEditingButton_, "I want to get back to editing");
                 
    this.closeButton_ = 
        $d('a', 
           {'href':'#', 
            'className': "mirosubs-green-button mirosubs-big"}, 
           "Ok, I'm done");
    goog.events.listen(this.closeButton_, "click",
                       goog.bind(this.onCloseClicked_, this));
    goog.dom.appendChild(this.contentDiv_, $d("div", "clearfix"));

    goog.dom.appendChild(this.contentDiv_, p );
    
    el.appendChild(this.contentDiv_);
    goog.dom.appendChild(el, this.closeButton_);
    goog.dom.appendChild(el, this.backToEditingButton_);
            
};


mirosubs.widget.droplockdialog.Dialog.prototype.onUpdateTimeDisplay_ = function(e){
    
    if (this.timeRemainingSpan_){
        goog.dom.setTextContent(this.timeRemainingSpan_, this.secondsUntilFreeze_ + " seconds");    
        this.secondsUntilFreeze_  -= 1;
        if (this.secondsUntilFreeze_ === 0){
            this.warningTimer_.stop();
            this.warningTimer_.disposeInternal();
            this.dispatchEvent(new mirosubs.widget.droplockdialog.SessionIdleEvent(this));
            this.createLockDroppedDom_();
            this.state = "DROPPED";
        }
    }
    
}

mirosubs.widget.droplockdialog.Dialog.prototype.onCloseClicked_ = function(e){
    e.preventDefault();
    this.dispatchEvent(new goog.events.Event("close", this));
    this.setVisible(false);
};

mirosubs.widget.droplockdialog.Dialog.prototype.onDownloadWorkClicked = function(e) {
    e.preventDefault();
    this.dispatchEvent(new mirosubs.widget.droplockdialog.DownloadRequestEvent (this));
    this.downloadPanel_ = new mirosubs.finishfaildialog.ErrorPanel(this.logger_);
};

mirosubs.widget.droplockdialog.Dialog.prototype.toMinutes = function(seconds) {
    return Math.ceil(seconds / 60);
}

mirosubs.widget.droplockdialog.Dialog.prototype.enterDocument = function() {
    mirosubs.widget.droplockdialog.Dialog.superClass_.enterDocument.call(this);
    //this.connectEvents_();
};

mirosubs.widget.droplockdialog.Dialog.prototype.onBackToEditing_ = function(e){
    this.warningTimer_.disposeInternal();
    this.dispatchEvent(new mirosubs.widget.droplockdialog.SessionResumedEvent(this));
    this.reset_();
    this.setVisible(false);
}

mirosubs.widget.droplockdialog.Dialog.SESSION_IDDLE = "SESSION_IDLE";
/**
* @constructor
* @param dialog {type} mirosubs.widget.droplockdialog.Dialog
*/
mirosubs.widget.droplockdialog.SessionIdleEvent = function(dialog) {
    this.type = mirosubs.widget.droplockdialog.Dialog.SESSION_IDDLE;
    this.dialog = dialog;
};


mirosubs.widget.droplockdialog.Dialog.SESSION_RESUMED = "SESSION_RESUMED";
/**
* @constructor
* @param dialog {type} mirosubs.widget.droplockdialog.Dialog
*/
mirosubs.widget.droplockdialog.SessionResumedEvent = function(dialog) {
    this.type = mirosubs.widget.droplockdialog.Dialog.SESSION_RESUMED;
    this.dialog = dialog;
};


mirosubs.widget.droplockdialog.Dialog.DOWNLOAD_REQUESTED = "DOWNLOAD_REQUESTED";
/**
* @constructor
* @param dialog {type} mirosubs.widget.droplockdialog.Dialog
*/
mirosubs.widget.droplockdialog.DownloadRequestEvent = function(dialog) {
    this.type = mirosubs.widget.droplockdialog.Dialog.DOWNLOAD_REQUESTED;
    this.dialog = dialog;
};
