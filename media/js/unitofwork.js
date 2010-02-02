goog.provide('mirosubs.UnitOfWork');
goog.provide('mirosubs.UnitOfWork.EventType');

mirosubs.UnitOfWork = function() {
    goog.events.EventTarget.call(this);
    this.instantiateLists_();
};
goog.inherits(mirosubs.UnitOfWork, goog.events.EventTarget);

mirosubs.UnitOfWork.EventType = {
    WORK_PERFORMED: 'workperformed'
};

mirosubs.UnitOfWork.prototype.instantiateLists_ = function() {
    this.updated = [];
    this.deleted = [];
    this.neu = [];
};

mirosubs.UnitOfWork.prototype.registerNew = function(obj) {
    if (goog.array.contains(this.updated, obj) ||
        goog.array.contains(this.deleted, obj) ||
        goog.array.contains(this.neu, obj))
        throw new "registerNew failed";
    this.neu.push(obj);
    this.issueWorkEvent_();
};

mirosubs.UnitOfWork.prototype.registerUpdated = function(obj) {
    if (goog.array.contains(this.deleted, obj))
        throw new "registerUpdated failed";
    if (!goog.array.contains(this.neu, obj) && 
        !goog.array.contains(this.updated, obj)) {
        this.updated.push(obj);
        this.issueWorkEvent_();
    }
};

mirosubs.UnitOfWork.prototype.registerDeleted = function(obj) {
    if (goog.array.contains(this.neu, obj))
        goog.array.remove(this.neu, obj);
    else {
        goog.array.remove(this.updated, obj);
        if (!goog.array.contains(this.deleted))
            this.deleted.push(obj);
        this.issueWorkEvent_();
    }
};

mirosubs.UnitOfWork.prototype.containsWork = function() {
    return this.updated.length > 0 || 
        this.deleted.length > 0 || 
        this.neu.length > 0;
};

mirosubs.UnitOfWork.prototype.clear = function() {
    this.instantiateLists_();
};

mirosubs.UnitOfWork.prototype.issueWorkEvent_ = function() {
    this.dispatchEvent(mirosubs.UnitOfWork.EventType.WORK_PERFORMED);
};

mirosubs.UnitOfWork.prototype.getWork = function() {
    var that = this;
    return {
        neu: goog.array.clone(that.neu),
        updated: goog.array.clone(that.updated),
        deleted: goog.array.clone(that.deleted) };
};
