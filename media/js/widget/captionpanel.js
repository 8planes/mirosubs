goog.provide('mirosubs.CaptionPanel');

mirosubs.CaptionPanel = function(videoID, videoPlayer, nullWidget) {
    goog.ui.Component.call(this);
    this.videoID_ = videoID;
    this.videoPlayer_ = videoPlayer;
    this.nullWidget_ = nullWidget;
    this.mainPanel_ = null;
};
goog.inherits(mirosubs.CaptionPanel, goog.ui.Component);

/**
 *
 * @param {function(boolean)} callback 
 */
mirosubs.CaptionPanel.prototype.startSubtitling = function(callback) {
    var that = this;

    if (this.nullWidget_) {
        callback(true);
        this.startSubtitlingNull_();
    }
    else    
        mirosubs.Rpc.call("start_editing", {"video_id": this.videoID_},
                          function(result) {
                              callback(result["can_edit"]);
                              if (result["can_edit"])
                                  that.startSubtitlingImpl_(result["version"], 
                                                            result["existing"]);
                              else {
                                  if (result["owned_by"])
                                      alert("Sorry, this video is owned by " + 
                                            result["owned_by"]);
                                  else
                                      alert("Sorry, this video is locked by " +
                                            result["locked_by"]);
                              }
                          });
};

mirosubs.CaptionPanel.prototype.startSubtitlingNull_ = function() {
    this.addChild(this.mainPanel_ = new mirosubs.subtitle
                  .MainPanel(this.videoPlayer_,
                             new mirosubs.subtitle.NullServerModel(),
                             []), true);
};

mirosubs.CaptionPanel.prototype.updateLoginState = function() {
    if (this.mainPanel_ != null) {
        if (mirosubs.currentUsername != null)
            this.mainPanel_.showLoggedIn(mirosubs.currentUsername);
        else
            this.mainPanel_.showLoggedOut();
    }
};

mirosubs.CaptionPanel.prototype.startSubtitlingImpl_ = 
    function(version, existingCaptions) {
    this.addChild(this.mainPanel_ = new mirosubs.subtitle
                  .MainPanel(this.videoPlayer_,
                             new mirosubs.subtitle.MSServerModel(this.videoID_,
                                                                 version),
                             existingCaptions),
                  true);
};

mirosubs.CaptionPanel.prototype.languageSelected = function(languageCode, captions) {
    this.removeChildren();
    if (this.playManager_)
        this.playManager_.dispose();
    this.playManager_ = new mirosubs.play.Manager(this.videoPlayer_, captions);
};

mirosubs.CaptionPanel.prototype.addNewLanguage = function(captions, languages) {
    this.addChild(new mirosubs.translate.MainPanel(
        this.videoPlayer_, this.videoID_, captions, languages), true);
};