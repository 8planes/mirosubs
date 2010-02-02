goog.provide('mirosubs.subtitle.LockManager');

mirosubs.subtitle.LockManager = function(lockMethod, lockArgs) {
    this.lockMethod_ = lockMethod;
    this.lockArgs_ = lockArgs;
    var that = this;
    this.timerInterval_ = window.setInterval(
        function() { that.updateLock_(); }, 
        (mirosubs.subtitle.LockManager.EXPIRATION - 10) * 1000);
};

// updated by values from server when widgets load.
mirosubs.subtitle.LockManager.EXPIRATION = 0;

mirosubs.subtitle.LockManager.prototype.updateLock_ = function() {
    mirosubs.Rpc.call(this.lockMethod_, this.lockArgs_);
};

mirosubs.subtitle.LockManager.prototype.dispose = function() {
    window.clearInterval(this.timerInterval_);
};