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

goog.provide('mirosubs.UserPanel');

/**
 * Wraps a few elements in the DOM for user-related info on widget.
 */

mirosubs.UserPanel = function(uuid) {
    goog.Disposable.call(this);
    var $ = goog.dom.$;
    this.mainPanel_ = $(uuid + "_topPanel");
    this.authenticatedPanel_ = $(uuid + "_authenticated");
    this.usernameSpan_ = $(uuid + "_username");
    this.notAuthenticatedPanel_ = $(uuid + "_notauthenticated");

    this.loginLink_ = $(uuid + '_login');
    this.logoutLink_ = $(uuid + '_logout');
    goog.events.listen(this.loginLink_, 'click', 
                       this.loginClicked_, false, this);
    goog.events.listen(this.logoutLink_, 'click', 
                       this.logoutClicked_, false, this);
};
goog.inherits(mirosubs.UserPanel, goog.Disposable);

mirosubs.UserPanel.prototype.setVisible = function(visible) {
    this.mainPanel_.style.display = visible ? '' : 'none';
};

mirosubs.UserPanel.prototype.setLoggedIn = function(username) {
    this.authenticatedPanel_.style.display = '';
    this.notAuthenticatedPanel_.style.display = 'none';
    goog.dom.setTextContent(this.usernameSpan_, username);
};

mirosubs.UserPanel.prototype.setLoggedOut = function() {
    this.authenticatedPanel_.style.display = 'none';
    this.notAuthenticatedPanel_.style.display = '';
};

mirosubs.UserPanel.prototype.loginClicked_ = function(event) {
    mirosubs.login();
    event.preventDefault();
};

mirosubs.UserPanel.prototype.logoutClicked_ = function(event) {
    mirosubs.logout();
    event.preventDefault();
};

mirosubs.UserPanel.prototype.disposeInternal = function() {
    mirosubs.UserPanel.superClass_.disposeInternal.call(this);
    goog.events.unlisten(this.loginLink_, 'click',
                         this.loginClicked_, false, this);
    goog.events.unlisten(this.logoutLink_, 'click',
                         this.logoutClicked_, false, this);
};