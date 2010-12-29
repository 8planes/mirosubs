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
 * @param {string} draftPK Universal Subtitles draft primary key
 * @param {string} videoID Universal Subtitles video id
 * @param {string} videoURL url for the video
 */
mirosubs.subtitle.MSServerModel = function(draftPK, videoID, videoURL) {
    goog.Disposable.call(this);
    this.draftPK_ = draftPK;
    this.videoID_ = videoID;
    this.videoURL_ = videoURL;
    this.initialized_ = false;
    this.finished_ = false;
    this.unsavedPackets_ = [];
    this.packetNo_ = 1;
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
};

mirosubs.subtitle.MSServerModel.prototype.finish = 
    function(jsonSubs, successCallback, opt_cancelCallback) 
{
    goog.asserts.assert(this.initialized_);
    goog.asserts.assert(!this.finished_);
    if (mirosubs.currentUsername == null) {
        if (!mirosubs.isLoginAttemptInProgress())
            mirosubs.login(
                function(loggedIn) {}, 
                "In order to finish and save your work, you need to log in.");
        if (opt_cancelCallback)
            opt_cancelCallback();
        return;
    }
    this.stopTimer_();
    var that = this;
    var saveArgs = this.makeSaveArgs_();
    mirosubs.Rpc.call(
        'finished_subtitles', 
        saveArgs,
        function(result) {
            if (result['response'] != 'ok')
                // this should never happen.
                alert('Problem saving subtitles. Response: ' +
                      result["response"]);
            that.finished_ = true;
            successCallback(mirosubs.widget.DropDownContents.fromJSON(
                result['drop_down_contents']));
        });
};

mirosubs.subtitle.MSServerModel.prototype.timerTick_ = function() {
    this.forceSave();
};

mirosubs.subtitle.MSServerModel.prototype.forceSave = function(opt_callback, opt_errorCallback) {
    var saveArgs = this.makeSaveArgs_();
    var that = this;
    mirosubs.Rpc.call(
        'save_subtitles',
        saveArgs, 
        function(result) {
            if (result['response'] != 'ok')
                // this should never happen.
                alert('Problem saving subtitles. Response: ' + 
                      result['response']);
            else {
                that.registerSavedPackets_(result['last_saved_packet']);
                if (opt_callback)
                    opt_callback();
            }
        },
        opt_errorCallback);
};

mirosubs.subtitle.MSServerModel.prototype.registerSavedPackets_ = 
    function(lastSavedPacketNo) 
{
    var saved = goog.array.filter(
        this.unsavedPackets_,
        function(p) { return p['packet_no'] <= lastSavedPacketNo; });
    for (var i = 0; i < saved.length; i++)
        goog.array.remove(this.unsavedPackets_, saved[i]);
};

mirosubs.subtitle.MSServerModel.prototype.makeSaveArgs_ = function() {
    var work = this.unitOfWork_.getWork();
    this.unitOfWork_.clear();
    this.unsavedPackets_ = goog.array.filter(
        this.unsavedPackets_,
        function(p) {
            return p['deleted'].length > 0 ||
                p['inserted'].length > 0 ||
                p['updated'].length > 0;
        });
    var toJson = mirosubs.subtitle.EditableCaption.toJsonArray;
    var packet = {
        'packet_no': this.packetNo_,
        'deleted': toJson(work.deleted),
        'inserted': toJson(work.neu),
        'updated': toJson(work.updated)
    };
    this.packetNo_++;
    this.unsavedPackets_.push(packet);
    return {
        'draft_pk': this.draftPK_,
        'packets': this.unsavedPackets_
    };
};

mirosubs.subtitle.MSServerModel.prototype.getEmbedCode = function() {
    return [
        '<sc',
        'ript type="text/javascript" src="',
        mirosubs.mediaURL(),
        'embed', mirosubs.embedVersion, '.js',
        '">\n',
        '({\n',
        '   video_url: "', this.videoURL_, '"\n',
        '})\n',
        '</script>'].join('');
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

mirosubs.subtitle.MSServerModel.prototype.getPermalink = function() {
    return [mirosubs.siteURL(), "/videos/", this.videoID_, "/info/"].join('');
};

mirosubs.subtitle.MSServerModel.prototype.getDraftPK = function() {
    return this.draftPK_;
};
