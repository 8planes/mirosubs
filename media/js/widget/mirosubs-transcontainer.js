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
mirosubs.trans.ContainerWidget = function(uuid, video_id, editVersion, playheadFn, 
                                          captionManager, existingCaptions, 
                                          opt_domHelper) {
    goog.ui.Component.call(this, opt_domHelper);
    this.uuid_ = uuid;
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
        return goog.array.map(arr, function(editableCaption) {
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
    this.lockManager_ = new mirosubs.trans.LockManager(
        'update_video_lock', { 'video_id' : video_id });
};
goog.inherits(mirosubs.trans.ContainerWidget, goog.ui.Component);

mirosubs.trans.ContainerWidget.prototype.createDom = function() {
    this.decorateInternal(this.dom_.createElement('div'));
};

mirosubs.trans.ContainerWidget.prototype.decorateInternal = function(element) {
    mirosubs.trans.ContainerWidget.superClass_.decorateInternal.call(this, element);
    goog.dom.classes.add(this.getElement(), 'MiroSubs-trans-container');
    var status = new goog.ui.Component();
    status.setElementInternal(goog.dom.createDom('div'));
    status.getElement().appendChild(goog.dom.createDom(
        'span', null, "Editing version " + this.editVersion_));
    status.getElement().innerHTML += "&nbsp;&nbsp;";
    var workIndicator = goog.dom.createDom('span');
    status.getElement().appendChild(workIndicator);
    this.addChild(status, true);

    this.saveManager_.setWorkIndicator(workIndicator);
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
    var nextWidget;
    if (state == 0)
        nextWidget = new mirosubs.trans.TransWidget(
            this.captions_, this.unitOfWork_);
    else if (state == 1)
        nextWidget = new mirosubs.trans.SyncWidget(
            this.captions_, this.playheadFn_, this.captionManager_);
    else if (state == 2)
        nextWidget = new mirosubs.trans.SyncWidget(
            this.captions_, this.playheadFn_, this.captionManager_);
    this.showInterPanel_(state, nextWidget);
};

mirosubs.trans.ContainerWidget.prototype.showInterPanel_ = function(state, nextWidget) {
    var that = this;
    var finishFn = function() {
        if (state < 3) {
            for (var i = 0; i < that.tabs_.length; i++)
                that.tabs_[i].getElement().setAttribute(
                    'class', i == state ? 'tab tab-selected' : 'tab');
            that.transcribeMain_.removeChildren();
            if (that.currentWidget != null)
                that.currentWidget.dispose();
            that.currentWidget = nextWidget;
            that.transcribeMain_.addChild(that.currentWidget, true);
            that.state_ = state;
        }
        else
            that.finishEditing_();
    };
    if (state != 0 && this.state_ == state - 1) {
        var panelElem = goog.dom.$(this.uuid_ + "_interPanel" + this.state_);
        var panelLink = goog.dom.$(this.uuid_ + "_interPanelLink" + this.state_);
        panelElem.style.display = '';
        goog.events.listenOnce(panelLink, 'click', function(event) {
                panelElem.style.display = 'none';
                finishFn();
                event.preventDefault();
            });
    } else
        finishFn();
};

mirosubs.trans.ContainerWidget.prototype.finishEditing_ = function() {
    
};

mirosubs.trans.ContainerWidget.prototype.disposeInternal = function() {
    this.saveManager_.dispose();
    this.lockManager_.dispose();
    mirosubs.trans.ContainerWidget.superClass_.disposeInternal.call(this);
};