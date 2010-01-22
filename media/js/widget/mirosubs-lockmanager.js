goog.provide('mirosubs.trans.LockManager');

mirosubs.trans.LockManager = function(lockMethod, lockArgs) {
    this.lockMethod_ = lockMethod;
    this.lockArgs_ = lockArgs;
    var that = this;
    this.timerInterval_ = window.setInterval(
        function() { that.updateLock_(); }, 
        (mirosubs.trans.LockManager.EXPIRATION - 10) * 1000);
};

// updated by values from server when widgets load.
mirosubs.trans.LockManager.EXPIRATION = 0;

mirosubs.trans.LockManager.prototype.updateLock_ = function() {
    mirosubs.Rpc.call(this.lockMethod_, this.lockArgs_);
};

mirosubs.trans.LockManager.prototype.dispose = function() {
    window.clearInterval(this.timerInterval_);
};