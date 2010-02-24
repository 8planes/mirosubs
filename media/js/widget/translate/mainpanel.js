goog.provide('mirosubs.translate.MainPanel');

mirosubs.translate.MainPanel = function(videoPlayer, videoID, subtitles, languages) {
    goog.ui.Component.call(this);
    this.videoID_ = videoID;
    this.subtitles_ = subtitles;
    this.languages_ = languages;
    this.unitOfWork_ = new mirosubs.UnitOfWork();
};
goog.inherits(mirosubs.translate.MainPanel, goog.ui.Component);

mirosubs.translate.MainPanel.prototype.getContentElement = function() {
    return this.contentElem_;
};

mirosubs.translate.MainPanel.prototype.createDom = function() {
    mirosubs.translate.MainPanel.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var selectOptions = [ $d('option', {'value':'NONE'}, 
                             'Select Language...') ];
    goog.array.forEach(this.languages_,
                       function(lang) {
                           selectOptions.push($d('option', 
                                                 {'value':lang['code']}, 
                                                 lang['name']));
                       });
    this.languageSelect_ = $d('select', null, selectOptions);
    this.getElement().appendChild(this.languageSelect_);
    this.getHandler().listen(this.languageSelect_, 
                             goog.events.EventType.CHANGE,
                             this.languageSelected_);
    this.getElement().appendChild(this.contentElem_ = $d('div'));
    this.addChild(this.translationList_ = 
                  new mirosubs.translate.TranslationList(this.subtitles_), 
                  true);
    this.translationList_.setEnabled(false);
};

mirosubs.translate.MainPanel.prototype.languageSelected_ = function(event) {
    var languageCode = this.languageSelect_.value;
    var that = this;
    // TODO: show loading animation
    this.translationList_.setEnabled(false);
    mirosubs.Rpc.call('start_translating', 
                      {'video_id' : this.videoID_, 
                       'language_code': languageCode },
                      function(result) {
                          // TODO: stop loading animation
                          if (result['can_edit'])
                              that.startEditing_(result['version'], 
                                                 result['existing']);
                          else
                              alert('locked by ' + result['locked_by']);
                      });
};

mirosubs.translate.MainPanel.prototype.startEditing_ = 
    function(version, existingTranslations) {
    var uw = this.unitOfWork_;
    var editableTranslations = 
        goog.array.map(existingTranslations, 
                       function(transJson) {
                           return new mirosubs.translate.EditableTranslation(
                               uw, transJson['caption_id'], transJson);
                       });
    this.translationList_.setTranslations(editableTranslations);
    this.translationList_.setEnabled(true);
};