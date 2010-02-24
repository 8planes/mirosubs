goog.provide('mirosubs.translate.TranslationWidget');

/**
 * Subtitle in json format
 */
mirosubs.translate.TranslationWidget = function(subtitle) {
    goog.ui.Component.call(this);
    this.subtitle_ = subtitle;
};
goog.inherits(mirosubs.translate.TranslationWidget, goog.ui.Component);

mirosubs.translate.TranslationWidget.prototype.createDom = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.setElementInternal($d('li', null,
                               $d('div', null, this.subtitle_['caption_text']),
                               this.translateInput_ = 
                               $d('input', {'type':'text'})));
};

/**
 *
 * @param {mirosubs.translate.EditableTranslation} translation
 */
mirosubs.translate.TranslationWidget.prototype.setTranslation = function(translation) {
    this.translation_ = translation;
    this.translateInput_.value = translation ? translation.getText() : '';
};

mirosubs.translate.TranslationWidget.prototype.getCaptionID = function() {
    return this.subtitle_['caption_id'];
};