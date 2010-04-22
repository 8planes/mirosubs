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
mirosubs.subtitle.MSServerModel = function(videoID, editVersion, isNull) {
    goog.Disposable.call(this);
    this.videoID_ = videoID;
    this.editVersion_ = editVersion;
    this.initialized_ = false;
    this.finished_ = false;
    this.isNull_ = isNull;
    this.loginPesterFreq_ = 1000 * 60 * (isNull ? 10 : 1);
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

mirosubs.subtitle.MSServerModel.prototype.init = function(unitOfWork, loginNagFn) {
    goog.asserts.assert(!this.initialized_);
    mirosubs.subtitle.MSServerModel.logger_.info(
        'init for ' + mirosubs.currentUsername);
    this.unitOfWork_ = unitOfWork;
    this.loginNagFn_ = loginNagFn;
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
            mirosubs.Rpc.call('finished_captions' + (that.isNull_ ? '_null' : ''), 
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
        if (!this.isNull_)
            mirosubs.Rpc.call("update_video_lock", 
                              { 'video_id': this.videoID_ });
        var currentTime = new Date().getTime();
        if (opt_forceLogin || 
            currentTime >= this.lastLoginPesterTime_ + this.loginPesterFreq_) {
            if (mirosubs.isLoginAttemptInProgress())
                return;
            this.lastLoginPesterTime_ = currentTime;
            if (opt_forceLogin) {
                alert("In order to finish and save your work, you need to log in.");
                mirosubs.login(action);
            }
            else
                this.loginNagFn_();
        }
    }
    else
        action();
};

mirosubs.subtitle.MSServerModel.prototype.saveImpl_ = function() {
    // TODO: at some point in future, account for possibly failed save.
    var $e = goog.json.serialize;
    var saveArgs = this.makeSaveArgs_();
    mirosubs.Rpc.call('save_captions' + (this.isNull_ ? '_null' : ''), 
                      saveArgs, 
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
    return [mirosubs.subtitle.MSServerModel.EMBED_JS_URL, 
            "?video_id=", this.videoID_].join('');
};

mirosubs.subtitle.MSServerModel.prototype.stopTimer_ = function() {
    if (this.timerRunning_) {
        window.clearInterval(this.timerInterval_);
        this.timerRunning_ = false;
    }
};

mirosubs.subtitle.MSServerModel.prototype.disposeInternal = function() {
    this.stopTimer_();
    this.loginNagFn_ = null;
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

mirosubs.subtitle.MSServerModel.prototype.getPermalink = function() {
    return [mirosubs.BASE_URL, "/videos/", this.videoID_, "/"].join('');
};