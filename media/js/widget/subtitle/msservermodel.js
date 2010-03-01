/**
 * @fileoverview ServerModel implementation for MiroSubs server.
 *
 */

goog.provide('mirosubs.subtitle.MSServerModel');

/**
 *
 *
 * @constructor
 * @implements {mirosubs.subtitle.ServerModel}
 * @extends {goog.Disposable}
 * @param {string} videoID MiroSubs videoid
 * @param {number} editVersion MiroSubs version number we are editing
 */
mirosubs.subtitle.MSServerModel = function(videoID, editVersion) {
    goog.Disposable.call(this);
    this.videoID_ = videoID;
    this.editVersion_ = editVersion;
    this.initialized_ = false;
    this.finished_ = false;
};
goog.inherits(mirosubs.subtitle.MSServerModel, goog.Disposable);

/*
 * URL for the widget's embed javascript.
 * Set by mirosubs.EmbeddableWidget when widget first loads.
 * @type {string} 
 */
mirosubs.subtitle.MSServerModel.EMBED_JS_URL = null;

mirosubs.subtitle.MSServerModel.logger_ = 
    goog.debug.Logger.getLogger('mirosubs.subtitle.MSServerModel');

// updated by values from server when widgets load.
mirosubs.subtitle.MSServerModel.LOCK_EXPIRATION = 0;

mirosubs.subtitle.MSServerModel.prototype.init = function(unitOfWork) {
    goog.asserts.assert(!this.initialized_);
    mirosubs.subtitle.MSServerModel.logger_.info(
        'init for ' + mirosubs.currentUsername);
    this.unitOfWork_ = unitOfWork;
    this.initialized_ = true;
    this.timerRunning_ = true;
    var that = this;
    this.timerInterval_ = 
    window.setInterval(function() {
            that.timerTick_();
        }, 
        (mirosubs.subtitle.MSServerModel.LOCK_EXPIRATION - 5) * 1000);
    this.lastLoginPesterTime_ = new Date().getTime();
};

mirosubs.subtitle.MSServerModel.prototype.finish = function(callback) {
    goog.asserts.assert(this.initialized_);
    goog.asserts.assert(!this.finished_);
    this.finished_ = true;
    this.stopTimer_();
    var that = this;
    this.loginThenAction_(function() {
            var $e = goog.json.serialize;
            var saveArgs = that.makeSaveArgs_();
            mirosubs.Rpc.call('finished_captions', 
                              saveArgs,
                              function(result) {
                                  if (result['response'] != 'ok')
                                      // this should never happen.
                                      alert('Problem saving subtitles. Response: ' +
                                            result["response"]);
                                  callback();
                              });
        }, true);
};

mirosubs.subtitle.MSServerModel.prototype.timerTick_ = function() {
    this.loginThenAction_(goog.bind(this.saveImpl_, this));
};

mirosubs.subtitle.MSServerModel.prototype.loginThenAction_ = 
    function(action, opt_forceLogin) {
    
    mirosubs.subtitle.MSServerModel.logger_.info(
        "loginThenAction_ for " + mirosubs.currentUsername);
    if (mirosubs.currentUsername == null) {
        // first update lock anyway.
        mirosubs.Rpc.call("update_video_lock", { 'video_id': this.videoID_ });
        var currentTime = new Date().getTime();
        if (opt_forceLogin || 
            currentTime >= this.lastLoginPesterTime_ + 60 * 1000) {
            if (mirosubs.isLoginDialogShowing())
                return;
            // temporary
            alert("We would like to save your captions, but before they get saved, " +
                  "you need to log in.");
            this.lastLoginPesterTime_ = currentTime;
            mirosubs.login(action);
        }
    }
    else
        action();
};

mirosubs.subtitle.MSServerModel.prototype.saveImpl_ = function() {
    // TODO: at some point in future, account for possibly failed save.
    var $e = goog.json.serialize;
    var saveArgs = this.makeSaveArgs_();
    mirosubs.Rpc.call('save_captions', saveArgs, 
                      function(result) {
                          if (result['response'] != 'ok')
                              // this should never happen.
                              alert('Problem saving subtitles. Response: ' + 
                                    result['response']);
                      });
};

mirosubs.subtitle.MSServerModel.prototype.makeSaveArgs_ = function() {
    var work = this.unitOfWork_.getWork();
    this.unitOfWork_.clear();
    var toJsonCaptions = function(arr) {
        return goog.array.map(arr, function(editableCaption) {
                return editableCaption.jsonCaption;
            });
    };
    return {
        'video_id': this.videoID_,
            'version_no': this.editVersion_,
            'deleted': toJsonCaptions(work.deleted),
            'inserted': toJsonCaptions(work.neu),
            'updated': toJsonCaptions(work.updated)
            };
};

mirosubs.subtitle.MSServerModel.prototype.getEmbedCode = function() {
    return mirosubs.subtitle.MSServerModel.EMBED_JS_URL + 
        "?video_id=" + this.videoID_;
};

mirosubs.subtitle.MSServerModel.prototype.stopTimer_ = function() {
    if (this.timerRunning_) {
        window.clearInterval(this.timerInterval_);
        this.timerRunning_ = false;
    }
};

mirosubs.subtitle.MSServerModel.prototype.disposeInternal = function() {
    this.stopTimer_();
};

mirosubs.subtitle.MSServerModel.prototype.currentUsername = function() {
    return mirosubs.currentUsername;
};

mirosubs.subtitle.MSServerModel.prototype.logIn = function() {
    mirosubs.login();
};

mirosubs.subtitle.MSServerModel.prototype.logOut = function() {
    mirosubs.logout();
};
