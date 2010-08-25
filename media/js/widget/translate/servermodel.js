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

goog.provide('mirosubs.translate.ServerModel');

// Currently this class has a lot in common with mirosubs.subtitle.MSServerModel.
// TODO: fix the duplication, probably by turning the two classes into one.

mirosubs.translate.ServerModel = function(videoID, unitOfWork, isNull, loginNagFn) {
    goog.Disposable.call(this);
    this.videoID_ = videoID;
    this.unitOfWork_ = unitOfWork;
    this.translating_ = false;
    this.isNull_ = isNull;
    this.loginNagFn_ = loginNagFn;
    this.loginPesterFreq_ = 1000 * 60 * (isNull ? 10 : 1);
};
goog.inherits(mirosubs.translate.ServerModel, goog.Disposable);

/**
 * 
 * @param {function(boolean, *)} calback. First arg is true iff successful, second 
 *     arg is string with failure message if failed, array of json translations 
 *     otherwise.
 */
mirosubs.translate.ServerModel.prototype.startTranslating = 
    function(languageCode, callback) 
{
    var that = this;
    this.stopTranslating();
    mirosubs.Rpc.call(
        'start_translating' + (this.isNull_ ? '_null' : ''),
        {'video_id': this.videoID_,
         'language_code': languageCode },
        function(result) {
            if (result['can_edit']) {
                that.startEditing_(languageCode, result['version']);
                callback(true, result['existing']);
            }
            else
                callback(false, 'locked by ' + result['locked_by']);
        });
};

mirosubs.translate.ServerModel.prototype.stopTranslating = function() {
    this.unitOfWork_.clear();
    this.curLanguageCode_ = null;
    this.curVersion_ = -1;
    this.translating_ = false;
    this.stopTimer_();
}

mirosubs.translate.ServerModel.prototype.startEditing =
    function(languageCode, version) 
{
    this.unitOfWork_.clear();
    this.startEditing_(languageCode, version);
}

mirosubs.translate.ServerModel.prototype.startEditing_ = 
    function(languageCode, version) {
    this.translating_ = true;
    this.curLanguageCode_ = languageCode;
    this.curVersion_ = version;
    this.timerRunning_ = true;
    this.finished_ = false;
    var that = this;
    this.timerInterval_ = 
    window.setInterval(function() {
            that.timerTick_();
        }, (mirosubs.subtitle.MSServerModel.LOCK_EXPIRATION - 5) * 1000);
    this.lastLoginPesterTime_ = new Date().getTime();
};

mirosubs.translate.ServerModel.prototype.timerTick_ = function() {
    if (!this.translating_)
        return;
    this.loginThenAction_(goog.bind(this.saveImpl_, this));
};

/**
 *
 *
 * @param {function(Object.<string, string>)} successCallback Function that takes 
 *     new available languages for video, in json format.
 * @param {function(Object.<string, string>)} opt_cancelCallback Optional function
 *     called if the login process is cancelled
 */
mirosubs.translate.ServerModel.prototype.finish = function(successCallback, opt_cancelCallback) {
    goog.asserts.assert(this.translating_);
    goog.asserts.assert(!this.finished_);
    this.stopTimer_();
    var that = this;
    this.loginThenAction_(function() {
        var saveArgs = that.makeSaveArgs_();
        mirosubs.Rpc.call('finished_translations' + 
                          (that.isNull_ ? '_null' : ''),
                          saveArgs,
                          function(result) {
                              if (result['response'] != 'ok')
                                  // should never happen
                                  alert('problem saving translations. response: ' +
                                        result['response']);
                              successCallback(result['available_languages']);
                          });
        }, opt_cancelCallback, true);
};

mirosubs.translate.ServerModel.prototype.loginThenAction_ = 
    function(successAction, opt_cancelAction, opt_forceLogin) {
    if (mirosubs.currentUsername == null) {
        // first update lock
        if (!this.isNull_)
            mirosubs.Rpc.call('update_video_translation_lock',
                              { 'video_id' : this.videoID_,
                                'language_code' : this.curLanguageCode_ });
        var currentTime = new Date().getTime();
        if (opt_forceLogin || 
            currentTime >= this.lastLoginPesterTime_ + this.loginPesterFreq_) {
            if (mirosubs.isLoginAttemptInProgress())
                return;            
            this.lastLoginPesterTime_ = currentTime;
            if (opt_forceLogin) {
                mirosubs.login(function(loggedIn) {
                    if (loggedIn)
                        successAction();
                    else if (opt_cancelAction)
                        opt_cancelAction();
                }, "In order to finish and save your work, you need to log in.");
            }
            else
                this.loginNagFn_();
        }
    }
    else
        successAction();
};

mirosubs.translate.ServerModel.prototype.saveImpl_ = function() {
    // TODO: at some point in the future, account for possibly failed save.
    var $s = goog.json.serialize;
    var saveArgs = this.makeSaveArgs_();
    mirosubs.Rpc.call('save_translations' + (this.isNull_ ? '_null' : ''), 
                      saveArgs,
                      function(result) {
                          if (result['response'] != 'ok')
                              // should never happen
                              alert('problem saving translations. Response: ' +
                                    result['response']);
                      });
};

mirosubs.translate.ServerModel.prototype.makeSaveArgs_ = function() {
    var work = this.unitOfWork_.getWork();
    this.unitOfWork_.clear();
    var toJsonTranslations = function(arr) {
        return goog.array.map(arr, function(editableTrans) {
                return editableTrans.jsonTranslation;
            });
    };
    return {
        'video_id': this.videoID_,
            'language_code': this.curLanguageCode_,
            'version_no' : this.curVersion_,
            'inserted': toJsonTranslations(work.neu),
            'updated' : toJsonTranslations(work.updated)
    };
};

mirosubs.translate.ServerModel.prototype.stopTimer_ = function() {
    if (this.timerRunning_) {
        window.clearInterval(this.timerInterval_);
        this.timerRunning_ = false;
    }
};

mirosubs.translate.ServerModel.prototype.disposeInternal = function() {
    this.stopTimer_();
};

mirosubs.translate.ServerModel.prototype.currentUsername = function() {
    return mirosubs.currentUsername;
};

mirosubs.translate.ServerModel.prototype.logIn = function() {
    mirosubs.login();
};

mirosubs.translate.ServerModel.prototype.logOut = function() {
    mirosubs.logout();
};