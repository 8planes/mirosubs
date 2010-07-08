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
 * @param {Array.<string>} extraHelp paragraphs to display in extra bubble. 
 *     0-length array will not display bubble.
 * @param {Array.<mirosubs.RightPanel.KeySpec>} legendKeySpecs
 * @param {boolean} showRestart
 * @param {string} doneStrongText
 * @param {string} doneText
 */
mirosubs.RightPanel = function(serverModel,
                               helpContents,
                               extraHelp,
                               legendKeySpecs,
                               showRestart,
                               doneStrongText,
                               doneText) {
    goog.ui.Component.call(this);
    this.serverModel_ = serverModel;
    this.helpContents_ = helpContents;
    this.extraHelp_ = extraHelp;
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
    BACK : 'back',
    GOTOSTEP : 'gotostep'
};
mirosubs.RightPanel.prototype.createDom = function() {
    mirosubs.RightPanel.superClass_.createDom.call(this);

    // TODO: you might really want to do this in enterDocument instead
    // of createDom, given that we're adding event listeners.

    var el = this.getElement();
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());

    this.appendHelpContentsInternal($d, el);

    this.appendExtraHelp_($d, el);

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
mirosubs.RightPanel.prototype.appendHelpContentsInternal = function($d, el) {
    var helpHeadingDiv = $d('div', 'mirosubs-help-heading');
    el.appendChild(helpHeadingDiv);
    helpHeadingDiv.appendChild($d('h2', null, this.helpContents_.header));
    if (this.helpContents_.numSteps) {
        var that = this;
        var stepsUL = $d('ul', null, $d('span', null, 'Steps'));
        for (var i = 0; i < this.helpContents_.numSteps; i++) {
            var linkAttributes = { 'href' : '#' };
            if (i == this.helpContents_.activeStep)
                linkAttributes['className'] = 'mirosubs-activestep';
            var link = $d('a', linkAttributes, i + 1 + '');
            var curStep = i;
            this.getHandler().listen(
                link, 'click', function(e) {
                    e.preventDefault();
                    that.dispatchEvent(
                        new mirosubs.RightPanel.GoToStepEvent(curStep));
                });
            stepsUL.appendChild($d('li', null, link));
        }
        helpHeadingDiv.appendChild(stepsUL);
    }
    goog.array.forEach(this.helpContents_.paragraphs, function(p) {
        el.appendChild($d('p', null, p));
    });
};
mirosubs.RightPanel.prototype.appendExtraHelp_ = function($d, el) {
    if (this.extraHelp_ && this.extraHelp_.length > 0) {
        var extraDiv = $d('div', 'mirosubs-extra');
        for (var i = 0; i < this.extraHelp_.length; i++)
            extraDiv.appendChild($d('p', null, this.extraHelp_[i]));
        extraDiv.appendChild($d('span', 'mirosubs-spanarrow'));
        el.appendChild(extraDiv);
    }
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
                          {'src': mirosubs.imageAssetURL('spinner.gif') });
    this.showLoading(false);
    this.doneAnchor_ = $d('a', {'className':'mirosubs-done', 'href':'#'},
                          $d('span', null,
                             this.loadingGif_,
                             $d('strong', null, this.doneStrongText_),
                             goog.dom.createTextNode(" "),
                             goog.dom.createTextNode(this.doneText_)));
    var stepsDiv = $d('div', 'mirosubs-steps', this.loginDiv_);

    this.backAnchor_ = 
        $d('a', {'className':'mirosubs-backTo mirosubs-greybutton', 'href':'#'}, 
           'Return to Typing');
    this.getHandler().listen(this.backAnchor_, 'click', this.backClickedInternal);
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

    stepsDiv.appendChild(this.doneAnchor_);
    
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
mirosubs.RightPanel.prototype.backClickedInternal = function(event) {
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
 * @constructor
 * Sets contents at top part of right panel.
 *
 * @param {string} header
 * @param {Array.<string>} paragraphs
 * @param {number=} opt_numSteps
 * @param {number} opt_activeStep;
 */
mirosubs.RightPanel.HelpContents = function(header, paragraphs, opt_numSteps, opt_activeStep) {
    this.header = header;
    this.paragraphs = paragraphs;
    this.numSteps = opt_numSteps;
    this.activeStep = opt_activeStep;
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
mirosubs.RightPanel.GoToStepEvent = function(stepNo) {
    this.type = mirosubs.RightPanel.EventType.GOTOSTEP;
    this.stepNo = stepNo;
};