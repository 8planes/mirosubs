goog.provide('mirosubs.subtitle.ReviewPanel');

mirosubs.subtitle.ReviewPanel = function(subtitles, videoPlayer, 
                                         captionManager, focusableElem) {
    mirosubs.subtitle.SyncPanel.call(this, subtitles, videoPlayer, 
                                     captionManager, focusableElem);
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
    return mirosubs.subtitle.SubtitleList.createHelpLi($d, helpLines, 
                                                       'Syncing Controls', 
                                                       true, 'BEGIN');
};