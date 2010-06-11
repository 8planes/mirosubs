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

goog.provide('mirosubs.EmbedWarning');

mirosubs.EmbedWarning = function(callback, left, top) {
    goog.ui.Dialog.call(this);

    this.setButtonSet(null);
    this.setDisposeOnHide(true);

    this.callback_ = callback;
    this.left_ = left;
    this.top_ = top;
};
goog.inherits(mirosubs.EmbedWarning, goog.ui.Dialog);

mirosubs.EmbedWarning.WARNING_COOKIE_NAME = "mirosubs_embed_warning_cleared";

mirosubs.EmbedWarning.prototype.createDom = function() {
    mirosubs.EmbedWarning.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var attrs = { 'className': 'mirosubs-link', 'href': '#' };
    var learnMoreAttrs = { 'className': 'mirosubs-link', 'target': '_blank',
                           'href': 'http://www.universalsubtitles.org' };
    var text = 'Note: this widget is in early testing stages.  ' +
        'Please only use it experimentally, with audiences that enjoy experiments.';
    this.continueLink_ = $d('a', attrs, 'Continue');
    this.learnMoreLink_ = $d('a', learnMoreAttrs, 'Learn More');
    this.cancelLink_ = $d('a', attrs, 'Cancel');

    this.getElement().className = "mirosubs-warning";
    this.getElement().appendChild($d('div', 'mirosubs-label', text));
    this.getElement().appendChild($d('div', 'mirosubs-buttons',
                                     this.continueLink_,
                                     this.learnMoreLink_,
                                     this.cancelLink_));
};
mirosubs.EmbedWarning.prototype.enterDocument = function() {
    mirosubs.EmbedWarning.superClass_.enterDocument.call(this);
    this.getHandler().
        listen(this.continueLink_,
               'click',
               this.continueLinkClicked_).
        listen(this.cancelLink_,
               'click',
               this.cancelLinkClicked_);

    goog.style.setPosition(this.getElement(), this.left_, this.top_);
};
mirosubs.EmbedWarning.prototype.showWarning = function() {
    if (this.isWarningCleared_()) {
        // if the warning has already been cleared and the cookie exists,
        // just go to the callback directly
        this.callback_();
    }
    else {
        this.setVisible(true);
    }
};
mirosubs.EmbedWarning.prototype.isWarningCleared_ = function() {
    return goog.net.cookies.isEnabled() &&
        goog.net.cookies.get(mirosubs.EmbedWarning.WARNING_COOKIE_NAME);
};
mirosubs.EmbedWarning.prototype.continueLinkClicked_ = function(event) {
    if (goog.net.cookies.isEnabled()) {
        goog.net.cookies.set(mirosubs.EmbedWarning.WARNING_COOKIE_NAME, "1", 86400);
    }
    this.callback_();
    this.setVisible(false);
    event.preventDefault();
};
mirosubs.EmbedWarning.prototype.cancelLinkClicked_ = function(event) {
    this.setVisible(false);
    event.preventDefault();
};