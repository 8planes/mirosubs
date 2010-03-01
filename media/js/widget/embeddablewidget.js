goog.provide('mirosubs.EmbeddableWidget');

mirosubs.EmbeddableWidget = function(uuid, videoID, youtubeVideoID, translationLanguages, 
                                     showTab, nullWidget) {
    goog.Disposable.call(this);

    var $ = goog.dom.$;

    if (youtubeVideoID == '')
        this.videoPlayer_ = mirosubs.Html5VideoPlayer.wrap(uuid + "_video");
    else
        this.videoPlayer_ = new mirosubs
            .YoutubeVideoPlayer(uuid, uuid + "_ytvideo", youtubeVideoID);
    this.userPanel_ = new mirosubs.UserPanel(uuid);
    this.controlTabPanel_ = new mirosubs.ControlTabPanel(uuid, showTab, videoID, 
                                                         translationLanguages);
    this.captionPanel_ = new mirosubs.CaptionPanel(videoID, 
                                                   this.videoPlayer_, 
                                                   nullWidget);
    this.captionPanel_.decorate($(uuid + "_captions"));
    this.handler_ = new goog.events.EventHandler(this);

    this.handler_.listen(this.controlTabPanel_, 
                         mirosubs.ControlTabPanel.EventType.SUBTITLEME_CLICKED,
                         this.startSubtitling_);
    this.handler_.listen(this.controlTabPanel_, 
                         mirosubs.ControlTabPanel.EventType.LANGUAGE_SELECTED,
                         this.languageSelected_);
    this.handler_.listen(this.controlTabPanel_,
                         mirosubs.ControlTabPanel.EventType.ADD_NEW_LANGUAGE,
                         this.addNewLanguage_);
};
goog.inherits(mirosubs.EmbeddableWidget, goog.Disposable);

mirosubs.EmbeddableWidget.logger_ =
    goog.debug.Logger.getLogger('mirosubs.EmbeddableWidget');

mirosubs.EmbeddableWidget.wrap = function(identifier) {
    var nullWidget = identifier["null_widget"];
    var debug = identifier["debug_js"];
    if (debug) {
        var debugWindow = new goog.debug.FancyWindow('main');
        debugWindow.setEnabled(true);
        debugWindow.init(); 
    }
    mirosubs.EmbeddableWidget.setConstants_(identifier);
    mirosubs.EmbeddableWidget.widgets = mirosubs.EmbeddableWidget.widgets || [];
    mirosubs.EmbeddableWidget.widgets.push(
        new mirosubs.EmbeddableWidget(identifier["uuid"], 
                                      identifier["video_id"],
                                      identifier["youtube_videoid"],
                                      identifier["translation_languages"],
                                      identifier["show_tab"],
                                      nullWidget));
};

mirosubs.EmbeddableWidget.setConstants_ = function(identifier) {
    var username = identifier["username"];
    mirosubs.EmbeddableWidget.logger_.info('username is ' + username);
    mirosubs.currentUsername = username == '' ? null : username;
    var baseURL = identifier["base_url"];
    mirosubs.subtitle.MainPanel.SPINNER_GIF_URL = 
        baseURL + '/site_media/images/spinner.gif';
    mirosubs.Rpc.BASE_URL = baseURL + '/widget/rpc/';
    mirosubs.BASE_LOGIN_URL = baseURL + '/widget/';
    mirosubs.subtitle.MSServerModel.EMBED_JS_URL = baseURL + '/embed_widget.js';
    mirosubs.subtitle.MSServerModel.LOCK_EXPIRATION = 
        identifier["writelock_expiration"];
};

mirosubs.EmbeddableWidget.prototype.updateLoginState = function() {
    if (mirosubs.currentUsername == null)
        this.userPanel_.setLoggedOut();
    else
        this.userPanel_.setLoggedIn(mirosubs.currentUsername);
    this.captionPanel_.updateLoginState();
};

mirosubs.EmbeddableWidget.prototype.startSubtitling_ = function() {
    this.controlTabPanel_.showLoading(true);
    var that = this;
    this.captionPanel_.startSubtitling(function(success) {
            that.controlTabPanel_.showLoading(false);
            if (success) {
                that.userPanel_.setVisible(false);
                goog.events.listenOnce(that.captionPanel_, 
                                       mirosubs.subtitle.MainPanel.EventType.FINISHED,
                                       that.finishedSubtitling_, false, that);
            }
        });
};

mirosubs.EmbeddableWidget.prototype.languageSelected_ = function(event) {
    this.captionPanel_.languageSelected(event.languageCode, event.captions);
};

mirosubs.EmbeddableWidget.prototype.addNewLanguage_ = function(event) {
    this.captionPanel_.addNewLanguage(event.captions, event.languages);
    this.userPanel_.setVisible(false);
    goog.events.listenOnce(this.captionPanel_,
                           mirosubs.translate.MainPanel.EventType.FINISHED,
                           this.finishedTranslating_, false, this);
};

mirosubs.EmbeddableWidget.prototype.finishedSubtitling_ = function(event) {
    this.controlTabPanel_.showSelectLanguage();
    this.userPanel_.setVisible(true);
};

mirosubs.EmbeddableWidget.prototype.finishedTranslating_ = function(event) {
    this.userPanel_.setVisible(true);
    this.controlTabPanel_.setAvailableLanguages(event.availableLanguages);
};

mirosubs.EmbeddableWidget.prototype.disposeInternal = function() {
    mirosubs.EmbeddableWidget.superClass_.disposeInternal.call(this);
    this.handler_.dispose();
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
