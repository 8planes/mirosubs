goog.provide('mirosubs.UserPanel');

/**
 * Wraps a few elements in the DOM for user-related info on widget.
 */

mirosubs.UserPanel = function(uuid) {
    goog.Disposable.call(this);
    var $ = goog.dom.$;
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