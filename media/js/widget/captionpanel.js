goog.provide('mirosubs.CaptionPanel');

mirosubs.CaptionPanel = function(videoID, videoPlayer) {
    goog.ui.Component.call(this);
    this.videoID_ = videoID;
    this.videoPlayer_ = videoPlayer;
};
goog.inherits(mirosubs.CaptionPanel, goog.ui.Component);

/**
 *
 * @param {function(boolean)} callback 
 */
mirosubs.CaptionPanel.prototype.startSubtitling = function(callback) {
    var that = this;
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

mirosubs.CaptionPanel.prototype.startSubtitlingImpl_ = 
    function(version, existingCaptions) {
    this.addChild(new mirosubs.subtitle
                  .MainPanel(this.videoPlayer_,
                             new mirosubs.subtitle.MSServerModel(this.videoID_,
                                                                 version),
                             existingCaptions),
                  true);
};

mirosubs.CaptionPanel.prototype.languageSelected = function(languageID, captions) {
    this.removeChildren();
    if (this.playManager_)
        this.playManager_.dispose();
    this.playManager_ = new mirosubs.play.Manager(this.videoPlayer_, captions);
};