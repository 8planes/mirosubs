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

goog.provide('mirosubs.RightPanel');

/**
 *
 * @param {mirosubs.ServerModel} serverModel
 * @param {mirosubs.RightPanel.HelpContents} helpContents
 * @param {Array.<mirosubs.RightPanel.KeySpec>} legendKeySpecs
 * @param {boolean} showRestart
 * @param {string} doneStrongText
 * @param {string} doneText
 */
mirosubs.RightPanel = function(serverModel,
                               helpContents,
                               legendKeySpecs,
                               showRestart,
                               doneStrongText,
                               doneText) {
    goog.ui.Component.call(this);
    this.serverModel_ = serverModel;
    this.helpContents_ = helpContents;
    this.legendKeySpecs_ = legendKeySpecs;
    this.showRestart_ = showRestart;
    this.doneStrongText_ = doneStrongText;
    this.doneText_ = doneText;
    this.loginDiv_ = null;
    this.doneAnchor_ = null;
    /**
     * Non-null iff the mouse has just been pressed on one of the legend keys
     * and not released or moved away from the legend key yet.
     * @type {?string}
     */
    this.mouseDownKeyCode_ = null;
};
goog.inherits(mirosubs.RightPanel, goog.ui.Component);
mirosubs.RightPanel.EventType = {
    LEGENDKEY : 'legend',
    RESTART : 'restart',
    DONE : 'done',
    BACK : 'back'
};
mirosubs.RightPanel.prototype.createDom = function() {
    mirosubs.RightPanel.superClass_.createDom.call(this);

    // TODO: you might really want to do this in enterDocument instead
    // of createDom, given that we're adding event listeners.

    var el = this.getElement();
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());

    this.appendHelpContents_($d, el);

    this.appendLegendContents_($d, el);

    this.appendStepsContents_($d, el);
};
mirosubs.RightPanel.prototype.showLoading = function(show) {
    this.loadingGif_.style.display = (show ? '' : 'none');
};
mirosubs.RightPanel.prototype.showBackLink = function(linkText) {
    this.backAnchor_.style.display = '';
    goog.dom.setTextContent(this.backAnchor_, linkText);
};
mirosubs.RightPanel.prototype.appendHelpContents_ = function($d, el) {
    var helpDiv = $d('div', 'mirosubs-help');
    el.appendChild(helpDiv);
    helpDiv.appendChild($d('h2', null, this.helpContents_.header));
    goog.array.forEach(this.helpContents_.paragraphs, function(p) {
        helpDiv.appendChild($d('p', null, p));
    });
    if (this.helpContents_.watchLinkText && this.helpContents_.watchLinkURL)
        helpDiv.appendChild(
            $d('a', {'className':'mirosubs-watch', 
                     'href':this.helpContents_.watchLinkURL},
               $d('span', null, this.helpContents_.watchLinkText)));
};
mirosubs.RightPanel.prototype.appendLegendContents_ = function($d, el) {
    var legendDiv = $d('div', 'mirosubs-legend');
    el.appendChild(legendDiv);
    this.appendLegendContentsInternal($d, legendDiv);
    this.appendLegendClearInternal($d, legendDiv);
};
mirosubs.RightPanel.prototype.appendLegendContentsInternal = function($d, legendDiv) {
    var et = goog.events.EventType;
    for (var i = 0; i < this.legendKeySpecs_.length; i++) {
        var spec = this.legendKeySpecs_[i];
        var key = $d('span', spec.spanClass, spec.keyText);
        legendDiv.appendChild(
            $d('div', spec.divClass,
               key, goog.dom.createTextNode(spec.legendText)));
        this.getHandler().listen(
            key, et.CLICK, goog.bind(this.legendKeyClicked_, 
                                     this, spec.keyCode));
        this.getHandler().listen(
            key, et.MOUSEDOWN, goog.bind(this.legendKeyMousedown_, 
                                         this, spec.keyCode));
        var mouseupFn = goog.bind(this.legendKeyMouseup_, this, spec.keyCode);
        this.getHandler().listen(key, et.MOUSEUP, mouseupFn);
        this.getHandler().listen(key, et.MOUSEOUT, mouseupFn);
    }
};
mirosubs.RightPanel.prototype.appendLegendClearInternal = function($d, legendDiv) {
    legendDiv.appendChild($d('div', 'mirosubs-clear'));    
};
mirosubs.RightPanel.prototype.appendStepsContents_ = function($d, el) {
    this.loginDiv_ = $d('div');
    this.loadingGif_ = $d('img', 
                          {'src': [mirosubs.BASE_URL, mirosubs.IMAGE_DIR, 
                                   'spinner.gif'].join('')});
    this.showLoading(false);
    this.doneAnchor_ = $d('a', {'className':'mirosubs-done', 'href':'#'},
                          $d('span', null,
                             this.loadingGif_,
                             $d('strong', null, this.doneStrongText_),
                             goog.dom.createTextNode(" "),
                             goog.dom.createTextNode(this.doneText_)));
    var stepsDiv = $d('div', 'mirosubs-steps',
                      this.loginDiv_, this.doneAnchor_);
    this.backAnchor_ = 
        $d('a', {'className':'mirosubs-backTo', 'href':'#'}, 
           'Back to Transcribe');
    this.getHandler().listen(this.backAnchor_, 'click', this.backClicked_);
    this.backAnchor_.style.display = 'none';
    stepsDiv.appendChild(this.backAnchor_);
    if (this.showRestart_) {
        var restartAnchor = 
            $d('a', {'className': 'mirosubs-restart','href':'#'}, 
               'Restart this Step');
        this.getHandler().listen(
            restartAnchor, 'click', this.restartClicked_);
        stepsDiv.appendChild(restartAnchor);
    }
    
    el.appendChild(stepsDiv);
    this.getHandler().listen(this.doneAnchor_, 'click', this.doneClicked_);
    this.updateLoginState();
};
mirosubs.RightPanel.prototype.legendKeyClicked_ = function(keyCode, event) {
    this.dispatchEvent(
        new mirosubs.RightPanel.LegendKeyEvent(keyCode, event.type));
};
mirosubs.RightPanel.prototype.legendKeyMousedown_ = function(keyCode, event) {
    this.dispatchEvent(
        new mirosubs.RightPanel.LegendKeyEvent(keyCode, event.type));
    this.mouseDownKeyCode_ = keyCode;
};
mirosubs.RightPanel.prototype.legendKeyMouseup_ = function(keyCode, event) {
    if (this.mouseDownKeyCode_ != null) {
        this.mouseDownKeyCode_ = null;
        this.dispatchEvent(
            new mirosubs.RightPanel.LegendKeyEvent(keyCode, 'mouseup'));
    }
};
mirosubs.RightPanel.prototype.backClicked_ = function(event) {
    this.dispatchEvent(mirosubs.RightPanel.EventType.BACK);
    event.preventDefault();
};
mirosubs.RightPanel.prototype.restartClicked_ = function(event) {
    this.dispatchEvent(mirosubs.RightPanel.EventType.RESTART);
    event.preventDefault();
};
mirosubs.RightPanel.prototype.doneClicked_ = function(event) {
    this.dispatchEvent(mirosubs.RightPanel.EventType.DONE);
    event.preventDefault();
};
mirosubs.RightPanel.prototype.getDoneAnchor = function() {
    return this.doneAnchor_;
};
mirosubs.RightPanel.prototype.updateLoginState = function() {
    goog.dom.removeChildren(this.loginDiv_);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    if (this.serverModel_.currentUsername() != null)
        this.loginDiv_.appendChild(
            $d('div', 'mirosubs-loggedIn',
               goog.dom.createTextNode(
                   ["You are logged in as ", 
                    this.serverModel_.currentUsername()].join(''))));
    else {
        var loginLink = $d('a', {'href':'#'}, "LOGIN");
        this.loginDiv_.appendChild(
            $d('div', 'mirosubs-needLogin',
               goog.dom.createTextNode(
                   'To save your subtitling work, you need to '),
               loginLink));
        this.getHandler().listen(loginLink, 'click', this.loginClicked_);
    }
};

mirosubs.RightPanel.prototype.loginClicked_ = function(event) {
    this.serverModel_.logIn();
    event.preventDefault();
};

/**
 * Sets contents at top part of right panel.
 *
 * @param {string} header
 * @param {Array.<string>} paragraphs
 * @param {string=} opt_watchLinkText
 * @param {string=} opt_watchLinkURL
 */
mirosubs.RightPanel.HelpContents = function(header, paragraphs, 
                                            opt_watchLinkText,
                                            opt_watchLinkURL) {
    this.header = header;
    this.paragraphs = paragraphs;
    this.watchLinkText = opt_watchLinkText;
    this.watchLinkURL = opt_watchLinkURL;
};
                                            
mirosubs.RightPanel.KeySpec = function(divClass, spanClass, 
                                       keyText, legendText, 
                                       keyCode) {
    this.divClass = divClass;
    this.spanClass = spanClass;
    this.keyText = keyText;
    this.legendText = legendText;
    this.keyCode = keyCode;
};
mirosubs.RightPanel.LegendKeyEvent = function(keyCode, eventType) {
    this.type = mirosubs.RightPanel.EventType.LEGENDKEY;
    this.keyCode = keyCode;
    this.keyEventType = eventType;
};
