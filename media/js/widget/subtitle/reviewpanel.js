goog.provide('mirosubs.subtitle.ReviewPanel');

mirosubs.subtitle.ReviewPanel = function(subtitles, playheadFn, isPausedFn, 
                                         captionManager) {
    mirosubs.subtitle.SyncPanel.call(this, subtitles, playheadFn, isPausedFn, 
                                     captionManager);
};
goog.inherits(mirosubs.subtitle.ReviewPanel, mirosubs.subtitle.SyncPanel);
/**
 * @override
 */
mirosubs.subtitle.ReviewPanel.prototype.createHelpDom = function($d) {
    var helpLines = ['Time to review your work.  Doubleclick on any text to edit it.',
                     ['To change subtitle timing, tap spacebar to skip to the next ',
                      'subtitle immediately.  To delay, press and hold spacebar to ',
                      'keep the next subtitle from displaying until you let go.'].join('')];
    return mirosubs.subtitle.Util.createHelpLi($d, helpLines, true, 'BEGIN');
};