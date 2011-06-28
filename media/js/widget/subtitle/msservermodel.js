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
 * @param {string} sessionPK Universal Subtitles subtitling session primary key
 * @param {string} videoID Universal Subtitles video id
 * @param {string} videoURL url for the video
 * @param {boolean} subsComplete Are we starting with a complete set of subs?
 * @param {mirosubs.subtitle.EditableCaptionSet} editableCaptionSet
 */
mirosubs.subtitle.MSServerModel = function(
    sessionPK, videoID, videoURL, 
    subsComplete, editableCaptionSet)
{
    goog.Disposable.call(this);
    this.sessionPK_ = sessionPK;
    this.videoID_ = videoID;
    this.videoURL_ = videoURL;
    this.subsComplete_ = subsComplete;
    this.captionSet_ = editableCaptionSet;
    this.initialized_ = false;
    this.finished_ = false;
    this.title_ = null;
    this.timerTickCount_ = 0;
    this.timer_ = new goog.Timer(
        (mirosubs.subtitle.MSServerModel.LOCK_EXPIRATION - 5) * 1000);
    goog.events.listen(
        this.timer_,
        goog.Timer.TICK,
        goog.bind(this.timerTick_, this));
    mirosubs.subtitle.MSServerModel.currentInstance = this;
};
goog.inherits(mirosubs.subtitle.MSServerModel, goog.Disposable);

mirosubs.subtitle.MSServerModel.currentInstance = null;

/*
 * URL for the widget's embed javascript.
 * Set by mirosubs.EmbeddableWidget when widget first loads.
 * @type {string} 
 */
mirosubs.subtitle.MSServerModel.EMBED_JS_URL = null;

// updated by values from server when widgets load.
mirosubs.subtitle.MSServerModel.LOCK_EXPIRATION = 0;

mirosubs.subtitle.MSServerModel.prototype.saveInitialSubs_ = function() {
    var savedSubs = new mirosubs.widget.SavedSubtitles(
        this.sessionPK_, null, this.subsComplete_, this.captionSet_);
    mirosubs.widget.SavedSubtitles.save(0, savedSubs);
};

/**
 * @return {?mirosubs.widget.SavedSubtitles}
 */
mirosubs.subtitle.MSServerModel.prototype.fetchInitialSubs_ = function() {
    return mirosubs.widget.SavedSubtitles.fetchSaved(0);
};

mirosubs.subtitle.MSServerModel.prototype.init = function() {
    goog.asserts.assert(!this.initialized_);
    this.initialized_ = true;
    this.saveInitialSubs_();
    this.startTimer();
};

mirosubs.subtitle.MSServerModel.prototype.startTimer = function() {
    this.timer_.start();
};

mirosubs.subtitle.MSServerModel.prototype.setTitle = function(title) {
    this.title_ = title;
};

mirosubs.subtitle.MSServerModel.prototype.timerTick_ = function(e) {
    mirosubs.Rpc.call(
        'regain_lock',
        { 'session_pk': this.sessionPK_  }, 
        function(result) {
            if (result['response'] != 'ok') {
                // this should never happen.
                alert("You lost the lock on these subtitles. This " +
                      "probably happened because your network connection disappeared for too long.");
            }
        },
        function() {
            // TODO: this means there was an error -- probably bad network connection.
            // we should communicate this to the user, since the user is in danger
            // of losing subtitling work.
        });
    this.timerTickCount_++;
    if ((this.timerTickCount_ % 4) == 0) {
        // for 2k subs, this takes about 20-40ms on FF and Chrome on my Macbook.
        var savedSubs = new mirosubs.widget.SavedSubtitles(
            this.sessionPK_, this.title_, null, this.captionSet_);
        mirosubs.widget.SavedSubtitles.save(1, savedSubs);
    }
};

mirosubs.subtitle.MSServerModel.prototype.makeFinishArgs_ = function(completed) {
    /**
     * @type {mirosubs.widget.SavedSubtitles}
     */
    var initialSubs = this.fetchInitialSubs_();

    var subtitles = null;
    if (!initialSubs.CAPTION_SET.identicalto(this.captionSet_))
        subtitles = this.captionSet_.nonblankSubtitles_();

    var args = { 'session_pk': this.sessionPK_ };
    var atLeastOneThingChanged = false;
    if (!goog.isNull(subtitles)) {
        args['subtitles'] = subtitles;
        atLeastOneThingChanged = true;
    }
    if (!goog.isNull(this.title_)) {
        args['new_title'] = this.title_;
        atLeastOneThingChanged = true;;
    }
    if (goog.isDefAndNotNull(completed) && completed != initialSubs.IS_COMPLETE) {
        args['completed'] = completed;
        atLeastOneThingChanged = true;
    }
    return atLeastOneThingChanged ? args : null;
};

mirosubs.subtitle.MSServerModel.prototype.finish = 
    function(successCallback, failureCallback, 
             opt_cancelCallback, opt_completed) 
{
    goog.asserts.assert(this.initialized_);
    goog.asserts.assert(!this.finished_);
    this.stopTimer();

    var that = this;
    var args = this.makeFinishArgs_(opt_completed);
    if (goog.isNull(args)) { // no changes.
        successCallback(); // TODO: is this the right ux?
        return;
    }
    mirosubs.Rpc.call(
        'finished_subtitles', 
        args,
        function(result) {
            if (result['response'] != 'ok') {
                // this should never happen.
                alert('Problem saving subtitles. Response: ' +
                      result["response"]);
                failureCallback(200);
            }
            else {
                that.finished_ = true;
                successCallback();
            }
        }, 
        function(opt_status) {
            failureCallback(opt_status);
        },
        true);
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

mirosubs.subtitle.MSServerModel.prototype.stopTimer = function() {
    this.timer_.stop();
};

mirosubs.subtitle.MSServerModel.prototype.disposeInternal = function() {
    mirosubs.subtitle.MSServerModel.superClass_.disposeInternal.call(this);
    this.stopTimer();
    this.timer_.dispose();
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

mirosubs.subtitle.MSServerModel.prototype.getVideoID = function() {
    return this.videoID_;
};

mirosubs.subtitle.MSServerModel.prototype.getSessionPK = function() {
    return this.sessionPK_;
};
