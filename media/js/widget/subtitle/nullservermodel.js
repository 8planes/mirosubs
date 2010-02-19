goog.provide('mirosubs.subtitle.NullServerModel');

mirosubs.subtitle.NullServerModel = function() {};

mirosubs.subtitle.NullServerModel.prototype.init = function(unitOfWork) {
    // do nothing!
};

mirosubs.subtitle.NullServerModel.prototype.finish = function(callback) {
    callback();
};

mirosubs.subtitle.NullServerModel.prototype.dispose = function() {
    // do nothing!
};

mirosubs.subtitle.NullServerModel.prototype.getEmbedCode = function() {
    return "NO EMBED FOR NULL WIDGET";
};

mirosubs.subtitle.NullServerModel.prototype.currentUsername = function() {
    return mirosubs.currentUsername;
};

mirosubs.subtitle.NullServerModel.prototype.logIn = function() {
    mirosubs.login();
};

mirosubs.subtitle.NullServerModel.prototype.logOut = function() {
    mirosubs.logout();
};