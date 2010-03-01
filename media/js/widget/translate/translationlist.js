goog.provide('mirosubs.translate.TranslationList');

/**
 *
 *
 * @param {mirosubs.UnitOfWork} unitOfWork Used to instantiate new EditableTranslations.
 */
mirosubs.translate.TranslationList = function(subtitles, unitOfWork) {
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
    this.unitOfWork_ = unitOfWork;
};
goog.inherits(mirosubs.translate.TranslationList, goog.ui.Component);

mirosubs.translate.TranslationList.prototype.createDom = function() {
    this.setElementInternal(this.getDomHelper()
                            .createDom('ul'));
    var that = this;
    var w;
    goog.array.forEach(this.subtitles_, 
                       function(subtitle) {
                           w = new mirosubs.translate.TranslationWidget(
                               subtitle, that.unitOfWork_);
                           that.addChild(w, true);
                           that.translationWidgets_.push(w);
                       });
};

mirosubs.translate.TranslationList.prototype.setEnabled = function(enabled) {
    goog.array.forEach(this.translationWidgets_,
                       function(widget) {
                           widget.setEnabled(enabled);
                       });
};

/**
 * This class will mutate the array as translations are added.
 * @param {Array.<mirosubs.translate.EditableTranslation>}
 */
mirosubs.translate.TranslationList.prototype.setTranslations = function(translations) {
    this.translations_ = translations;
    var i, translation;
    var map = {};
    for (i = 0; i < translations.length; i++)
        map[translations[i].getCaptionID()] = translations[i];
    for (i = 0; i < this.translationWidgets_.length; i++) {
        translation = map[this.translationWidgets_[i].getCaptionID()];
        this.translationWidgets_[i].setTranslation(translation ? translation : null);
    }
};