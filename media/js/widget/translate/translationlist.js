goog.provide('mirosubs.translate.TranslationList');

mirosubs.translate.TranslationList = function(subtitles) {
    goog.ui.Component.call(this);
    /**
     * Array of subtitles in json format
     */
    this.subtitles_ = subtitles;
    /**
     * @type {Array.<mirosubs.translate.TranslationWidget>}
     */
    this.translationWidgets_ = [];
    this.translations_ = [];
};
goog.inherits(mirosubs.translate.TranslationList, goog.ui.Component);

mirosubs.translate.TranslationList.prototype.createDom = function() {
    this.setElementInternal(this.getDomHelper()
                            .createDom('ul'));
    var that = this;
    var w;
    goog.array.forEach(this.subtitles_, 
                       function(subtitle) {
                           w = new mirosubs.translate.TranslationWidget(subtitle)
                               that.addChild(w, true);
                           that.translationWidgets_.push(w);
                       });
};

mirosubs.translate.TranslationList.prototype.setEnabled = function(enabled) {
    
};

/**
 * This class will mutate the array as translations are added.
 * @param {Array.<mirosubs.translate.EditableTranslation>}
 */
mirosubs.translate.TranslationList.prototype.setTranslations = function(translations) {
    this.translations_ = translations;
    var i;
    var translation;
    var map = {};
    for (i = 0; i < translations.length; i++)
        map[translations[i].getCaptionID()] = translations[i];
    for (i = 0; i < this.translationWidgets_.length; i++) {
        translation = map[this.translationWidgets_[i].getCaptionID()];
        this.translationWidgets_[i].setTranslation(translation ? translation : null);
    }
};