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