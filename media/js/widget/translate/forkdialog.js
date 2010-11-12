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

goog.provide('mirosubs.translate.ForkDialog');

/**
 * @constructor
 * @param {number} draftPK
 * @param {string} languageCode
 * @param {function(mirosubs.widget.SubtitleState)} finishedCallback Called 
 *     after forking has occurred on server.
 */
mirosubs.translate.ForkDialog = function(draftPK, languageCode, finishedCallback) {
    goog.ui.Dialog.call(this, 'mirosubs-forkdialog', true);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this.draftPK_ = draftPK;
    this.languageCode_ = languageCode;
    this.finishedCallback_ = finishedCallback;
};
goog.inherits(mirosubs.translate.ForkDialog, goog.ui.Dialog);

mirosubs.translate.ForkDialog.prototype.createDom = function() {
    mirosubs.translate.ForkDialog.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var language = mirosubs.languageNameForCode(this.languageCode_);
    this.getElement().appendChild(
        $d('div', null,
           $d('p', null, 'Are you sure you want to edit timing?'),
           $d('p', null, 
              'Advanced users only!  Most subtitles should keep original ' +
              'timing. You can edit this timing on the ' + language + 
              ' subtitle page. (Where ' + language + 
              ' is the language of original subtitles). ' +
              'If unsure, click cancel now.'),
           $d('p', null,
              'If you continue, you should finish all translations first ' +
              '(the original text will not be visible on the next screen).')));
    this.okButton_ =
        $d('a',
           {'href':'#',
            'className': 'mirosubs-green-button mirosubs-big'},
           'Continue');
    this.getElement().appendChild(this.okButton_);
    var clearDiv = $d('div', {'style': 'clear: both'});
    clearDiv.innerHTML = "&nbsp;";
    this.getElement().appendChild(clearDiv);
};

mirosubs.translate.ForkDialog.prototype.enterDocument = function() {
    mirosubs.translate.ForkDialog.superClass_.enterDocument.call(this);
    this.getHandler().
        listen(this.okButton_,
               'click',
               this.okClicked_);
};

mirosubs.translate.ForkDialog.prototype.okClicked_ = function(e) {
    e.preventDefault();
    mirosubs.Rpc.call(
        'fork',
        {'draft_pk': this.draftPK_},
        goog.bind(this.okResponse_, this));
};

mirosubs.translate.ForkDialog.prototype.okResponse_ = function(result) {
    this.setVisible(false);
    this.finishedCallback_(mirosubs.widget.SubtitleState.fromJSON(result));
};