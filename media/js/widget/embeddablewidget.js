goog.provide('mirosubs.EmbeddableWidget');

mirosubs.EmbeddableWidget = function(uuid, videoID, showTab) {
    goog.Disposable.call(this);

    var $ = goog.dom.$;

    this.videoPlayer_ = mirosubs.VideoPlayer.wrap(uuid + "_video");
    this.userPanel_ = new mirosubs.UserPanel(uuid);
    this.controlTabPanel_ = new mirosubs.ControlTabPanel(uuid, showTab, videoID);
    this.captionPanel_ = new mirosubs.CaptionPanel(videoID, this.videoPlayer_);
    this.captionPanel_.decorate($(uuid + "_captions"));

    goog.events.listen(this.controlTabPanel_, 
                       mirosubs.ControlTabPanel.EventType.SUBTITLEME_CLICKED,
                       this.startSubtitling_,
                       false, this);
    goog.events.listen(this.controlTabPanel_, 
                       mirosubs.ControlTabPanel.EventType.LANGUAGE_SELECTED,
                       this.languageSelected_,
                       false, this);
};
goog.inherits(mirosubs.EmbeddableWidget, goog.Disposable);

mirosubs.EmbeddableWidget.wrap = function(identifier) {
    mirosubs.EmbeddableWidget.setConstants_(identifier);
    mirosubs.EmbeddableWidget.widgets = mirosubs.EmbeddableWidget.widgets || [];
    mirosubs.EmbeddableWidget.widgets.push(
        new mirosubs.EmbeddableWidget(identifier["uuid"], 
                                      identifier["video_id"], 
                                      identifier["show_tab"]));
};

mirosubs.EmbeddableWidget.setConstants_ = function(identifier) {
    var username = identifier["username"];
    mirosubs.currentUsername = username == '' ? null : username;
    mirosubs.Rpc.BASE_URL = identifier["base_rpc_url"];
    mirosubs.BASE_LOGIN_URL = identifier["base_login_url"];
    mirosubs.subtitle.LockManager.EXPIRATION = identifier["writelock_expiration"];
};

mirosubs.EmbeddableWidget.prototype.updateLoginState = function() {
    if (mirosubs.currentUsername == null)
        this.userPanel_.setLoggedOut();
    else
        this.userPanel_.setLoggedIn(mirosubs.currentUsername);
};

mirosubs.EmbeddableWidget.prototype.startSubtitling_ = function() {
    this.controlTabPanel_.showLoading(true);
    var that = this;
    this.captionPanel_.startSubtitling(function(success) {
            that.controlTabPanel_.showLoading(false);
            if (success) {
                that.controlTabPanel_.setVisible(false);
                goog.events.listenOnce(that.captionPanel_, 
                                       mirosubs.subtitle.MainPanel.EventType.FINISHED,
                                       that.finishedSubtitling_, false, that);
            }
        });
};

mirosubs.EmbeddableWidget.prototype.languageSelected_ = function(event) {
    this.captionPanel_.languageSelected(event.languageID, event.captions);
};

mirosubs.EmbeddableWidget.prototype.finishedSubtitling_ = function(event) {
    this.controlTabPanel_.showSelectLanguage();
    this.controlTabPanel_.setVisible(true);
};

mirosubs.EmbeddableWidget.prototype.disposeInternal = function() {
    mirosubs.EmbeddableWidget.superClass_.disposeInternal.call(this);
    goog.events.removeAll(this.controlTabPanel_);
};

// see http://code.google.com/closure/compiler/docs/api-tutorial3.html#mixed
mirosubs["EmbeddableWidget"] = mirosubs.EmbeddableWidget;
mirosubs.EmbeddableWidget["wrap"] = mirosubs.EmbeddableWidget.wrap;

(function() {
    var m = window["MiroSubsToEmbed"];
    if (typeof(m) != 'undefined')
        for (var i = 0; i < m.length; i++)
            mirosubs.EmbeddableWidget.wrap(m[i]);
})();
