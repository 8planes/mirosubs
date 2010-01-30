goog.provide('mirosubs.CaptionWidget');

// TODO: have this inherit from goog.ui.Component

mirosubs.CaptionWidget = function(uuid, videoID, showTab, username) {
    var that = this;
    this.uuid_ = uuid;
    this.videoID_ = videoID;

    mirosubs.currentUsername = username == '' ? null : username;
    
    mirosubs.CaptionWidget.widgets = mirosubs.CaptionWidget.widgets || [];
    mirosubs.CaptionWidget.widgets.push(this);

    this.userPanel_ = new mirosubs.CaptionWidget.UserPanel_(uuid);

    this.unitOfWork = new mirosubs.UnitOfWork();
    this.captionDiv_ = goog.dom.$(uuid + "_captions");    
    this.videoPlayer = mirosubs.VideoPlayer.wrap(uuid + "_video");
    this.playheadFn_ = function() {
            return that.videoPlayer.getPlayheadTime();
        };
    // TODO: dispose of this during disposal after inheriting from goog.ui.Component.
    var onClick = function(id, listener) {
        goog.events.listen(goog.dom.$(id), 'click', listener, false, that);
    };

    if (showTab == 0 || showTab == 1)
        onClick(uuid + (showTab == 0 ? "_tabSubtitleMe" : "_tabContinue"), 
                this.subtitleMeListener_);
    var tabSelectLanguageID = uuid + "_tabSelectLanguage";
    this.tabSelectLanguageElem_ = goog.dom.$(tabSelectLanguageID);
    onClick(tabSelectLanguageID, this.languageSelectedListener_);
};

mirosubs.CaptionWidget.wrap = function(identifier) {
    var uuid = identifier["uuid"];
    var videoID = identifier["video_id"];
    var showTab = identifier["show_tab"];
    var username = identifier["username"];
    mirosubs.Rpc.BASE_URL = identifier["base_rpc_url"];
    mirosubs.BASE_LOGIN_URL = identifier["base_login_url"];
    mirosubs.trans.LockManager.EXPIRATION = identifier["writelock_expiration"];
    new mirosubs.CaptionWidget(uuid, videoID, showTab, username);
};

mirosubs.CaptionWidget.prototype.updateLoginState = function() {
    if (mirosubs.currentUsername == null)
        this.userPanel_.setLoggedOut();
    else
        this.userPanel_.setLoggedIn(mirosubs.currentUsername);
};

mirosubs.CaptionWidget.prototype.captionReached_ = function(jsonCaptionEvent) {
    var c = jsonCaptionEvent.caption;
    this.videoPlayer.showCaptionText(c ? c['caption_text'] : '');
};

mirosubs.CaptionWidget.prototype.languageSelectedListener_ = function(event) {
    goog.dom.removeChildren(this.captionDiv_);
    var that = this;
    var languageSelectionWidget = new mirosubs.CaptionDisplayWidget(
        this.videoPlayer, this.videoID_, this.playheadFn_);
    languageSelectionWidget.decorate(this.captionDiv_);
    event.preventDefault();
};

mirosubs.CaptionWidget.prototype.subtitleMeListener_ = function(event) {
    var that = this;
    var loadingImage = goog.dom.$(this.uuid_ + "_loading");
    loadingImage.style.display = '';
    mirosubs.Rpc.call("start_editing", {"video_id": this.videoID_},
                      function(result) {
                          loadingImage.style.display = 'none';
                          if (!result["can_edit"]) {
                              if (result["owned_by"])
                                  alert("Sorry, this video is owned by " + 
                                        result["owned_by"]);
                              else
                                  alert("Sorry, this video is locked by " +
                                        result["locked_by"]);
                          }
                          else {
                              that.startEditing_(result["version"], 
                                                 result["existing"]);
                          }
                      });
    event.preventDefault();
};

mirosubs.CaptionWidget.prototype.startEditing_ = 
    function(version, existingCaptions) {
    // TODO: It makes more sense to instantiate the captionManager 
    // from within the containerWidget.
    this.captionManager_ = new mirosubs.CaptionManager(this.playheadFn_);
    this.captionManager_.addEventListener(mirosubs.CaptionManager.CAPTION_EVENT,
                                          this.captionReached_, false, this);
    this.captionManager_.addCaptions(
        goog.array.filter(existingCaptions,
                          function(caption) {
                              return caption['start_time'] != -1;
                          }));
    goog.dom.removeChildren(this.captionDiv_);
    var containerWidget = new mirosubs.trans.ContainerWidget(
        this.videoPlayer, this.uuid_,
        this.videoID_, version, this.playheadFn_, this.captionManager_, 
        existingCaptions);
    containerWidget.decorate(this.captionDiv_);
    containerWidget.addEventListener(
        mirosubs.trans.ContainerWidget.EventType.FINISHED_EDITING,
        this.finishedEditing_, false, this);
};

mirosubs.CaptionWidget.prototype.finishedEditing_ = function(event) {
    goog.dom.removeChildren(this.captionDiv_);
    this.captionDiv_.appendChild(this.tabSelectLanguageElem_);
    this.tabSelectLanguageElem_.style.display = '';
    // TODO: It makes more sense to instantiate the captionManager 
    // from within the containerWidget.
    this.captionManager_.dispose();
    this.captionManager_ = null;
};

/**
 * A private class to manage the user div in the widget.
 */
mirosubs.CaptionWidget.UserPanel_ = function(uuid) {
    var $ = goog.dom.$;
    this.authenticatedPanel_ = $(uuid + "_authenticated");
    this.usernameSpan_ = $(uuid + "_username");
    this.notAuthenticatedPanel_ = $(uuid + "_notauthenticated");

    goog.events.listen($(uuid + '_login'), 'click', 
                       this.loginClicked_, false, this);
    goog.events.listen($(uuid + '_logout'), 'click', 
                       this.logoutClicked_, false, this);
};

mirosubs.CaptionWidget.UserPanel_.prototype.setLoggedIn = function(username) {
    this.authenticatedPanel_.style.display = '';
    this.notAuthenticatedPanel_.style.display = 'none';
    goog.dom.setTextContent(this.usernameSpan_, username);
};

mirosubs.CaptionWidget.UserPanel_.prototype.setLoggedOut = function() {
    this.authenticatedPanel_.style.display = 'none';
    this.notAuthenticatedPanel_.style.display = '';
};

mirosubs.CaptionWidget.UserPanel_.prototype.loginClicked_ = function(event) {
    mirosubs.login();
    event.preventDefault();
};

mirosubs.CaptionWidget.UserPanel_.prototype.logoutClicked_ = function(event) {
    mirosubs.logout();
    event.preventDefault();
};

// see http://code.google.com/closure/compiler/docs/api-tutorial3.html#mixed
mirosubs["CaptionWidget"] = mirosubs.CaptionWidget;
mirosubs.CaptionWidget["wrap"] = mirosubs.CaptionWidget.wrap;

(function() {
    var m = window["MiroSubsToEmbed"];
    if (typeof(m) != 'undefined')
        for (var i = 0; i < m.length; i++)
            mirosubs.CaptionWidget.wrap(m[i]);
})();
