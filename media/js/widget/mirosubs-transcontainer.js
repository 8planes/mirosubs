goog.provide('mirosubs.trans.ContainerWidget');

/**
 * @fileoverview In this class, the three states {0, 1, 2} correspond to 
 *     { transcribe, sync, review }.
 */

/**
 *
 * @param {int} editVersion The caption version we're editing.
 * @param {Function} playheadFn Function that returns current playhead time for video.
 * @param {mirosubs.CaptionManager} Caption manager, already containing any captions that 
 *     exist and have startTime set.
 * @param {array.<jsonCaptions>} existing captions in json object format.
 */
mirosubs.trans.ContainerWidget = function(video_id, editVersion, playheadFn, captionManager, existingCaptions, opt_domHelper) {
    goog.ui.Component.call(this, opt_domHelper);
    var uw = this.unitOfWork_ = new mirosubs.UnitOfWork();
    /**
     * Array of captions.
     * @type {Array.<mirosubs.trans.EditableCaption>}
     */
    this.captions_ = 
        goog.array.map(existingCaptions, 
                       function(caption) { 
                           return new mirosubs.trans.EditableCaption(uw, caption);
                       });
    this.tabs_ = [];
    this.playheadFn_ = playheadFn;
    this.captionManager_ = captionManager;
    this.editVersion_ = editVersion;
    var toJsonCaptions = function(arr) {
        goog.array.map(arr, function(editableCaption) {
                return editableCaption.jsonCaption;
            });
    };
    this.saveManager_ = new mirosubs.trans.SaveManager(
        uw, "save_captions", function(work) {
            return {
                "video_id" : video_id,
                "version_no" : editVersion,
                "deleted" : toJsonCaptions(work.deleted),
                "inserted" : toJsonCaptions(work.neu),
                "updated" : toJsonCaptions(work.updated)
            };
        });
};
goog.inherits(mirosubs.trans.ContainerWidget, goog.ui.Component);

mirosubs.trans.ContainerWidget.prototype.createDom = function() {
    this.decorateInternal(this.dom_.createElement('div'));
};

mirosubs.trans.ContainerWidget.prototype.decorateInternal = function(element) {
    mirosubs.trans.ContainerWidget.superClass_.decorateInternal.call(this, element);
    goog.dom.classes.add(this.getElement(), 'MiroSubs-trans-container');
    var versionLabel = new goog.ui.Component();
    versionLabel.setElementInternal(
        goog.dom.createDom('div', null, 
                           "Editing version " + this.editVersion_));
    this.addChild(versionLabel, true);
    this.addChild(this.transcribeMain_ = new goog.ui.Component(), true);
    goog.dom.classes.add(this.transcribeMain_.getElement(), 'main');
    var buttonContainer = new goog.ui.Component();
    this.addChild(buttonContainer, true);
    var that = this;
    goog.array.forEach(["Transcribe", "Sync", "Review"],
                       function(text, index) {
                           buttonContainer.addChild(that.createTab_(text, index), true);
                       });
    this.addChild(this.nextStepButton_ = new goog.ui.Button("Next Step >>"), true);
    goog.events.listen(this.nextStepButton_, goog.ui.Component.EventType.ACTION,
                       function(e) {
                           if (that.state_ < 2)
                               that.setState_(that.state_ + 1);
                       });
    this.setState_(0);
};

mirosubs.trans.ContainerWidget.prototype.createTab_ = function(text, index) {
    var tab = new goog.ui.Button(text);
    this.tabs_[index] = tab;
    var that = this;
    goog.events.listen(tab, goog.ui.Component.EventType.ACTION,
                       function(e) {
                           that.setState_(index);
                       });
    return tab;
};

mirosubs.trans.ContainerWidget.prototype.setState_ = function(state) {
    var that = this;
    this.state_ = state;
    for (var i = 0; i < this.tabs_.length; i++)
        this.tabs_[i].getElement().setAttribute(
            'class', i == state ? 'tab tab-selected' : 'tab');
    this.transcribeMain_.removeChildren();
    if (this.currentWidget != null)
        this.currentWidget.dispose();
    if (state == 0)
        this.currentWidget = new mirosubs.trans.TransWidget(
            this.captions_, this.unitOfWork_);
    else if (state == 1)
        this.currentWidget = new mirosubs.trans.SyncWidget(
            this.captions_, this.playheadFn_, this.captionManager_);
    else if (state == 2)
        this.saveCaptioningWork_(function() {
                that.currentWidget = new mirosubs.trans.TranslationWidget(
                    that.captions_, that.captionManager_);
            });
    this.transcribeMain_.addChild(this.currentWidget, true);
};

mirosubs.trans.ContainerWidget.prototype.disposeInternal = function() {
    this.saveManager_.dispose();
    mirosubs.trans.ContainerWidget.superClass_.disposeInternal.call(this);
};