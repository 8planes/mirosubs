goog.provide('mirosubs.trans.SaveManager');

/**
 *
 * @param saveArgStrategy {Function} a function that takes the work object from 
 *     a {mirosubs.UnitOfWork} and transforms it into an argument associative 
 *     array suitable for passing to mirosubs.Rpc.call.
 */
mirosubs.trans.SaveManager = function(unitOfWork, saveMethod, saveArgStrategy) {
    this.unitOfWork_ = unitOfWork;
    this.saveMethod_ = saveMethod;
    this.saveArgStrategy = saveArgStrategy;
    goog.events.listen(unitOfWork, mirosubs.UnitOfWork.WORK_EVENT,
                       this.workPerformed_, false, this);
    this.workIndicator_ = null;

    var makeLabel = function(label) {
        var comp = new goog.ui.Component();
        comp.setElementInternal(goog.dom.createDom('span', null, label));
        return comp;
    };

    this.savingChild_ = makeLabel("Saving...");
    this.savedChild_ = makeLabel("Saved");
    this.saveNowChild_ = new goog.ui.Component();
    this.saveNowChild_.setElementInternal(
        goog.dom.createDom('a', {'href': '#'}, "Save now"));
    goog.events.listen(this.saveNowChild_, 'click', 
                       this.saveNowClicked_, false, this);
    this.currentChild_ = null;
    this.saving_ = false;
};

mirosubs.trans.SaveManager.prototype.saveNowClicked_ = function(event) {
    this.saveNow();
    event.preventDefault();
};

mirosubs.trans.SaveManager.prototype.saveNow = function(opt_finishFn) {
    if (!this.unitOfWork_.containsWork())
        return;
    if (mirosubs.currentUsername == null) {
        if (mirosubs.isLoginDialogShowing())
            return;
        // temporary
        alert("We would like to save your captions, but before they get saved, " +
              "you need to log in.");
        var that = this;
        mirosubs.login(function() { that.saveImpl_(opt_finishFn); });
    }
    else
        this.saveImpl_(opt_finishFn);
};

mirosubs.trans.SaveManager.prototype.saveImpl_ = function(opt_finishFn) {
    var work = this.unitOfWork_.getWork();
    this.unitOfWork_.clear();
    this.saving_ = true;
    this.setChild_(this.savingChild_);
    var that = this;
    mirosubs.Rpc.call(this.saveMethod_, this.saveArgStrategy_(work),
                      function(result) {
                          if (opt_finishFn != null)
                              opt_finishFn(result);
                          that.saving_ = false;
                          if (that.unitOfWork_.containsWork())
                              that.setChild_(that.saveNowChild_);
                          else
                              that.setChild_(that.savedChild_);
                      });
};

mirosubs.trans.SaveManager.prototype.workPerformed_ = function(event) {
    if (!this.saving_)
        this.setChild_(this._saveNowChild);
};

mirosubs.trans.SaveManager.prototype.setWorkIndicator = function(workIndicator) {
    this.workIndicator_ = workIndicator;
    if (this.currentChild_ != null)
        this.workIndicator_.addChild(this.currentChild_);
};

mirosubs.trans.SaveManager.prototype.setChild_ = function(child) {
    if (this.workIndicator_ != null &&
        this.currentChild_ != child) {
        this.workIndicator_.removeChildren();
        this.workIndicator_.addChild(child);
    }
    this.currentChild_ = child;
};

mirosubs.trans.SaveManager.prototype.dispose = function() {
    // TODO: remove event listeners from constructor. Stop timer.
};