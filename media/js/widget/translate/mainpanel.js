goog.provide('mirosubs.translate.MainPanel');

mirosubs.translate.MainPanel = function(videoPlayer, videoID, subtitles, 
                                        languages, nullWidget) {
    goog.ui.Component.call(this);
    this.videoID_ = videoID;
    this.subtitles_ = subtitles;
    this.languages_ = languages;
    this.unitOfWork_ = new mirosubs.UnitOfWork();
    this.serverModel_ = new mirosubs.translate.ServerModel(
        videoID, this.unitOfWork_, nullWidget);
};
goog.inherits(mirosubs.translate.MainPanel, goog.ui.Component);

mirosubs.translate.MainPanel.prototype.getContentElement = function() {
    return this.contentElem_;
};

mirosubs.translate.MainPanel.prototype.createLanguageSelect_ = function($d) {
    var selectOptions = [ $d('option', {'value':'NONE'}, 
                             'Select Language...') ];
    goog.array.forEach(this.languages_,
                       function(lang) {
                           selectOptions.push($d('option', 
                                                 {'value':lang['code']}, 
                                                 lang['name']));
                       });
    return $d('select', null, selectOptions);
};

mirosubs.translate.MainPanel.prototype.createDom = function() {
    mirosubs.translate.MainPanel.superClass_.createDom.call(this);
    var el = this.getElement();
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    el.appendChild(this.languageSelect_ = this.createLanguageSelect_($d));
    this.getHandler().listen(this.languageSelect_, 
                             goog.events.EventType.CHANGE,
                             this.languageSelected_);
    el.appendChild(this.contentElem_ = $d('div'));
    var finishAnchorElem;
    el.appendChild($d('div', {'className':'mirosubs-nextStep'},
                      this.logInOutLink_ = $d('a', {'className':'mirosubs-logoutLink',
                                                    'href':'#'}),
                      this.loadingGif_ = $d('img', {'style':'display: none',
                                                    'alt':'loading',
                                                    'src':mirosubs.subtitle.MainPanel
                                                         .SPINNER_GIF_URL}),
                      finishAnchorElem = $d('a', { 'href': '#'}, 
                         "Done? ",
                         $d('strong', null, 'Submit Translation'))));
    this.getHandler().listen(finishAnchorElem, 'click', this.finishClicked_);
    this.getHandler().listen(this.logInOutLink_, 'click', this.logInOutClicked_);
    if (this.serverModel_.currentUsername() != null)
        this.showLoggedIn(this.serverModel_.currentUsername());
    else
        this.showLoggedOut();
    this.addChild(this.translationList_ = 
                  new mirosubs.translate.TranslationList(this.subtitles_, 
                                                         this.unitOfWork_), 
                  true);
    this.translationList_.setEnabled(false);
};

mirosubs.translate.MainPanel.prototype.languageSelected_ = function(event) {
    var languageCode = this.languageSelect_.value;
    var that = this;
    // TODO: show loading animation
    this.translationList_.setEnabled(false);
    this.serverModel_.startTranslating(languageCode, 
        function(success, result) {
            if (!success)
                alert(result);
            else
                that.startEditing_(result);
        });
};

mirosubs.translate.MainPanel.prototype.startEditing_ = 
    function(existingTranslations) {
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

mirosubs.translate.MainPanel.prototype.finishClicked_ = function(event) {
    var that = this;
    this.serverModel_.finish(function(availableLanguages) {
            that.dispatchEvent(new mirosubs.translate.MainPanel
                               .FinishedEvent(availableLanguages));
            that.dispose();
        });
    event.preventDefault();
};

mirosubs.translate.MainPanel.prototype.logInOutClicked_ = function(event) {
    if (this.loggedIn_)
        this.serverModel_.logOut();
    else
        this.serverModel_.logIn();
    event.preventDefault();
};

mirosubs.translate.MainPanel.prototype.showLoggedIn = function(username) {
    this.loggedIn_ = true;
    goog.dom.setTextContent(this.logInOutLink_, "Logout " + username);
};

mirosubs.translate.MainPanel.prototype.showLoggedOut = function() {
    this.loggedIn_ = false;
    goog.dom.setTextContent(this.logInOutLink_, "Login");
};

mirosubs.translate.MainPanel.prototype.disposeInternal = function() {
    mirosubs.translate.MainPanel.superClass_.disposeInternal.call(this);
    this.serverModel_.dispose();
};

mirosubs.translate.MainPanel.EventType = {
    FINISHED : 'translateFinished'
};

mirosubs.translate.MainPanel.FinishedEvent = function(availableLanguages) {
    this.type = mirosubs.translate.MainPanel.EventType.FINISHED;
    this.availableLanguages = availableLanguages;
};