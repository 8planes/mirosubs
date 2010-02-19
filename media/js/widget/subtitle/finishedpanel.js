goog.provide('mirosubs.subtitle.FinishedPanel');

/**
 * 
 * @param {mirosubs.subtitle.ServerModel} serverModel
 */
mirosubs.subtitle.FinishedPanel = function(serverModel) {
    goog.ui.Component.call(this);
    this.serverModel_ = serverModel;
};
goog.inherits(mirosubs.subtitle.FinishedPanel, goog.ui.Component);
mirosubs.subtitle.FinishedPanel.prototype.createDom = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var embedCodeInput = $d('input', {'type':'text'});
    var helpLi = $d('li', null, 
                    $d('p', null, 
                       ['Thanks for submitting. Now anyone else who views ',
                        'this video can see your work.'].join('')),
                    $d('p', null, 
                       ['To share it with others, or post on your site, ',
                        'use this embed code'].join('')),
                    embedCodeInput);
    embedCodeInput['value'] = this.serverModel_.getEmbedCode();
    this.setElementInternal($d('ul', {'className':'mirosubs-titlesList'},
                               helpLi));
};