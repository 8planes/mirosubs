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
    this.logger_ = new mirosubs.subtitle.Logger(draftPK);
};
goog.inherits(mirosubs.subtitle.MSServerModel, goog.Disposable);

/*
 * URL for the widget's embed javascript.
 * Set by mirosubs.EmbeddableWidget when widget first loads.
 * @type {string} 
 */
mirosubs.subtitle.MSServerModel.EMBED_JS_URL = null;

// updated by values from server when widgets load.
mirosubs.subtitle.MSServerModel.LOCK_EXPIRATION = 0;

mirosubs.subtitle.MSServerModel.prototype.init = function(unitOfWork) {
    goog.asserts.assert(!this.initialized_);
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

mirosubs.subtitle.MSServerModel.prototype.setTitle_ = function() {
    var args  = {};
    args['draft_pk'] = this.draftPK_;
    args['value'] = this.unitOfWork_.title;
    mirosubs.Rpc.call('set_title', args);

};

mirosubs.subtitle.MSServerModel.prototype.getSubIDPackets_ = function() {
    return goog.array.map(
        this.unsavedPackets_, function(p) { return p.subIDPacket; });
};

mirosubs.subtitle.MSServerModel.prototype.finish = 
    function(jsonSubs, successCallback, failureCallback, 
             opt_cancelCallback, opt_completed) 
{
    this.setTitle_();
    goog.asserts.assert(this.initialized_);
    goog.asserts.assert(!this.finished_);
    this.stopTimer_();
    var that = this;
    var saveArgs = this.makeSaveArgs_();
    if (goog.isDefAndNotNull(opt_completed))
        saveArgs['completed'] = opt_completed;
    this.logger_.setJsonSubs(jsonSubs);
    var subIDPackets = this.getSubIDPackets_();
    mirosubs.Rpc.call(
        'finished_subtitles', 
        saveArgs,
        function(result) {
            if (result['response'] != 'ok') {
                // this should never happen.
                alert('Problem saving subtitles. Response: ' +
                      result["response"]);
                that.logger_.logSave(subIDPackets, false, response);
                failureCallback(that.logger_, 200);
            }
            else {
                that.finished_ = true;
                successCallback(new mirosubs.widget.DropDownContents(
                    result['drop_down_contents']));
            }
        }, 
        function(opt_status) {
            that.logger_.logSave(subIDPackets, false);
            failureCallback(that.logger_, opt_status);
        },
        true);
};

mirosubs.subtitle.MSServerModel.prototype.timerTick_ = function() {
    this.forceSave();
};

mirosubs.subtitle.MSServerModel.prototype.forceSave = function(opt_callback, opt_errorCallback) {
    var that = this;
    var saveArgs = this.makeSaveArgs_();
    var subIDPackets = this.getSubIDPackets_();

    mirosubs.Rpc.call(
        'save_subtitles',
        saveArgs, 
        function(result) {
            if (result['response'] != 'ok') {
                // this should never happen.
                alert('Problem saving subtitles. Response: ' + 
                      result['response']);
                that.logger_.logSave(
                    subIDPackets, false, result['response']);
            }
            else {
                that.logger_.logSave(subIDPackets, true);
                that.registerSavedPackets_(result['last_saved_packet']);
                if (opt_callback)
                    opt_callback();
            }
        },
        function() {
            that.logger_.logSave(subIDPackets, false);
            if (opt_errorCallback)
                opt_errorCallback();
        });
};

mirosubs.subtitle.MSServerModel.prototype.registerSavedPackets_ = 
    function(lastSavedPacketNo) 
{
    var saved = goog.array.filter(
        this.unsavedPackets_,
        function(p) { return p.packetNo <= lastSavedPacketNo; });
    for (var i = 0; i < saved.length; i++)
        goog.array.remove(this.unsavedPackets_, saved[i]);
};

mirosubs.subtitle.MSServerModel.prototype.makePacket_ = function(work, f) {
    return {
        'packet_no': this.packetNo_,
        'deleted': f(work.deleted),
        'inserted': f(work.inserted),
        'updated': f(work.updated)
    };
};

mirosubs.subtitle.MSServerModel.prototype.makeSaveArgs_ = function() {
    var containsWork = this.unitOfWork_.containsWork();
    var work = this.unitOfWork_.getWork();
    this.unitOfWork_.clear();
    if (containsWork) {
        var packet = this.makePacket_(
            work, mirosubs.subtitle.EditableCaption.toJsonArray);
        var subIDPacket = this.makePacket_(
            work, mirosubs.subtitle.EditableCaption.toIDArray);
        this.packetNo_++;
        this.unsavedPackets_.push({
            packetNo: this.packetNo_,
            packet: packet,
            subIDPacket: subIDPacket
        });
    }
    var args = {
        'draft_pk': this.draftPK_,
        'packets': goog.array.map(
            this.unsavedPackets_, function(p) { return p.packet; })
    };
    if (window['UNISUBS_THROW_EXCEPTION'])
        args['throw_exception'] = true;
    return args;
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
