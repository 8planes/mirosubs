goog.provide('mirosubs.subtitle.SaveManager');

/**
 *
 * @param saveArgStrategy {Function} a function that takes the work object from 
 *     a {mirosubs.UnitOfWork} and transforms it into an argument associative 
 *     array suitable for passing to mirosubs.Rpc.call.
 */
mirosubs.subtitle.SaveManager = function(unitOfWork, saveMethod, saveArgStrategy) {
    goog.Disposable.call(this);
    this.unitOfWork_ = unitOfWork;
    this.saveMethod_ = saveMethod;
    this.saveArgStrategy_ = saveArgStrategy;
    this.saving_ = false;
    var that = this;
    this.timerInterval_ = window.setInterval(
        function() { that.saveNow(); }, 30 * 1000);
    this.lastLoginPesterTime_ = new Date().getTime();
};
goog.inherits(mirosubs.subtitle.SaveManager, goog.Disposable);

mirosubs.subtitle.SaveManager.prototype.saveNow = function(opt_finishFn) {
    if (this.saving_ || !this.unitOfWork_.containsWork()) {
        if (opt_finishFn != null)
            opt_finishFn();
        return;
    }
    if (mirosubs.currentUsername == null) {
        var currentTime = new Date().getTime();
        if (currentTime >= this.lastLoginPesterTime_ + 60 * 1000) {
            if (mirosubs.isLoginDialogShowing())
                return;
            // temporary
            alert("We would like to save your captions, but before they get saved, " +
                  "you need to log in.");
            this.lastLoginPesterTime_ = currentTime;
            var that = this;
            mirosubs.login(function() { that.saveImpl_(opt_finishFn); });
        }
    }
    else
        this.saveImpl_(opt_finishFn);
};

mirosubs.subtitle.SaveManager.prototype.saveImpl_ = function(opt_finishFn) {
    var work = this.unitOfWork_.getWork();
    this.unitOfWork_.clear();
    this.saving_ = true;
    var that = this;
    mirosubs.Rpc.call(this.saveMethod_, this.saveArgStrategy_(work),
                      function(result) {
                          if (opt_finishFn != null)
                              opt_finishFn(result);
                          that.saving_ = false;
                      });
};


mirosubs.subtitle.SaveManager.prototype.disposeInternal = function() {
    mirosubs.subtitle.SaveManager.superClass_.disposeInternal.call(this);
    window.clearInterval(this.timerInterval_);
};