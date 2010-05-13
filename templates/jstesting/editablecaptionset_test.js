{% extends "jstesting/base_test.html" %}
{% block testscript %}

var MS_eventHandler = new goog.events.EventHandler();
var MS_updatedCaptions = [];
var MS_cleared = false;
var MS_unitOfWork = null;

function MS_updateListener(event) {
    MS_updatedCaptions.push(event.target);
}
function MS_clearListener(event) {
    MS_cleared = true;
}
/* A couple helper functions. */
function captionJSON(start_time, end_time, caption_id) {
    return {'start_time' : start_time, 'end_time': end_time, 'caption_id': caption_id};
}

function listenToCaption(editableCaption) {
    MS_eventHandler.listen(
        editableCaption,
        mirosubs.subtitle.EditableCaption.CHANGE,
        MS_updateListener);
}

function addNewCaption(set) {
    var c = set.addNewCaption();
    listenToCaption(c);
    return c;
}

function createSet(existingCaptions) {    
    MS_unitOfWork = new mirosubs.UnitOfWork();
    var captionSet = new mirosubs.subtitle.EditableCaptionSet(
        existingCaptions, MS_unitOfWork);
    for (var i = 0; i < captionSet.count(); i++)
        listenToCaption(captionSet.caption(i));
    MS_eventHandler.listen(
        captionSet, 
        mirosubs.subtitle.EditableCaptionSet.CLEAR_ALL,
        MS_clearListener);
    return captionSet;
};

function tearDown() {
    MS_eventHandler.removeAll();
    MS_updatedCaptions = [];
    MS_cleared = false;
    MS_unitOfWork = null;
}

function testBasicAdd() {
    var set = createSet([]);
    addNewCaption(set);
    addNewCaption(set);
    addNewCaption(set);
    assertEquals(3, set.count());
}

function testBasicSetTime() {
    var set = createSet([]);
    var caption0 = addNewCaption(set);
    var caption1 = addNewCaption(set);
    var minLength = mirosubs.subtitle.EditableCaption.MIN_LENGTH;
    assertEquals(0, MS_updatedCaptions.length);
    caption0.setStartTime(0.3);
    assertEquals(1, MS_updatedCaptions.length);
    assertEquals(0.3, caption0.getStartTime());
    assertTrue(caption0.getEndTime() == -1);
    assertEquals(-1, caption1.getStartTime());
    assertEquals(caption0, MS_updatedCaptions[0]);
}

function testSetTimeTooClose() {
    var set = createSet([]);
    var caption0 = addNewCaption(set);
    var caption1 = addNewCaption(set);
    var FIRSTTIME = 0.3;
    caption0.setStartTime(FIRSTTIME);
    // imitates hitting spacebar too early in sync view.
    caption1.setStartTime(
        FIRSTTIME + mirosubs.subtitle.EditableCaption.MIN_LENGTH / 2);
    assertEquals(FIRSTTIME, caption0.getStartTime());
    assertEquals(FIRSTTIME + mirosubs.subtitle.EditableCaption.MIN_LENGTH,
                 caption0.getEndTime());
    assertEquals(caption0.getEndTime(), caption1.getStartTime());
    assertTrue(caption1.getEndTime() == -1);
    assertEquals(3, MS_updatedCaptions.length);
}

function assertMinMaxTimes(caption, minStart, maxStart, minEnd, maxEnd) {
    assertEquals(minStart, caption.getMinStartTime());
    if (maxStart == null)
        assertTrue(caption.getMaxStartTime() > 9999);
    else
        assertEquals(maxStart, caption.getMaxStartTime());
    assertEquals(minEnd, caption.getMinEndTime());
    if (maxEnd == null)
        assertTrue(caption.getMaxEndTime() > 9999);
    else
        assertEquals(maxEnd, caption.getMaxEndTime());
}

function testMinMaxTimes() {
    // set times, make sure min/max times make sense.
    var set = createSet([]);
    var caption0 = addNewCaption(set);
    var caption1 = addNewCaption(set);
    var caption2 = addNewCaption(set);
    var minLength = mirosubs.subtitle.EditableCaption.MIN_LENGTH;
    
    var T0 = 1.8, T1 = 5.6, T2 = 9.2;

    caption0.setStartTime(T0);
    assertMinMaxTimes(caption0, 0, null, T0 + minLength, null);
    assertEquals(1, MS_updatedCaptions.length);

    caption1.setStartTime(T1);
    assertMinMaxTimes(caption0, 0, T1 - minLength, T0 + minLength, null);
    assertMinMaxTimes(caption1, T0 + minLength, null, T1 + minLength, null);
    assertEquals(T1 + minLength, caption2.getMinStartTime());
    assertEquals(3, MS_updatedCaptions.length);

    caption2.setStartTime(T2);
    assertMinMaxTimes(caption0, 0, T1 - minLength, 
                      T0 + minLength, T2 - minLength);
    assertMinMaxTimes(caption1, T0 + minLength, T2 - minLength, 
                      T1 + minLength, null);
    assertMinMaxTimes(caption2, T1 + minLength, null, T2 + minLength, null);
    assertEquals(5, MS_updatedCaptions.length);
}

function testExistingCaptions() {
    var T0 = 1.8, T1 = 5.6, T2 = 9.2;
    var set = createSet([
        captionJSON(T0, T1, 1),
        captionJSON(T1, T2, 2), 
        captionJSON(T2, -1, 3)]);
    var minLength = mirosubs.subtitle.EditableCaption.MIN_LENGTH;
    assertMinMaxTimes(set.caption(0), 0, T1 - minLength, 
                      T0 + minLength, T2 - minLength);
    assertMinMaxTimes(set.caption(1), T0 + minLength, T2 - minLength, 
                      T1 + minLength, null);
    assertMinMaxTimes(set.caption(2), T1 + minLength, null, 
                      T2 + minLength, null);
    assertEquals(0, MS_updatedCaptions.length);
}

function testSpacebarHold() {
    var T0 = 1.8, T1 = 5.6, T2 = 9.2;
    var set = createSet([
        captionJSON(T0, T1, 1),
        captionJSON(T1, T2, 2), 
        captionJSON(T2, 99999, 3)]);
    var minLength = mirosubs.subtitle.EditableCaption.MIN_LENGTH;
    // imitating space bar held in middle of first caption.
    set.caption(0).setEndTime(T2 + 2);
    assertEquals(T0, set.caption(0).getStartTime());
    assertEquals(T2 + 2, set.caption(0).getEndTime());
    assertEquals(T2 + 2, set.caption(1).getStartTime());
    assertEquals(T2 + 2 + minLength, set.caption(1).getEndTime());
    assertEquals(T2 + 2 + minLength, set.caption(2).getStartTime());
    assertTrue(set.caption(2).getEndTime() > 9999);
    assertEquals(3, MS_updatedCaptions.length);
}

function testSpacebarHoldForFirst() {
    var T0 = 1.8, T1 = 5.6, T2 = 9.2;
    var set = createSet([
        captionJSON(T0, T1, 1),
        captionJSON(T1, T2, 2), 
        captionJSON(T2, 99999, 3)]);
    var minLength = mirosubs.subtitle.EditableCaption.MIN_LENGTH;
    // imitating space bar held before start of first caption.
    set.caption(0).setStartTime(T1 + 2);
    assertEquals(T1 + 2, set.caption(0).getStartTime());
    assertEquals(T1 + 2 + minLength, set.caption(0).getEndTime());
    assertEquals(T1 + 2 + minLength, set.caption(1).getStartTime());
    assertEquals(Math.max(T1 + 2 + minLength * 2, T2), 
                 set.caption(1).getEndTime());
    assertEquals(Math.max(T1 + 2 + minLength * 2, T2), 
                 set.caption(2).getStartTime()) ;
    assertTrue(set.caption(2).getEndTime() > 9999);
    assertEquals(3, MS_updatedCaptions.length);
}

function testClearAll() {
    var T0 = 1.8, T1 = 5.6, T2 = 9.2;
    var set = createSet([
        captionJSON(T0, T1, 1),
        captionJSON(T1, T2, 2), 
        captionJSON(T2, 99999, 3)]);
    set.clear();
    assertEquals(0, set.count());
    assertTrue(MS_cleared);
    var work = MS_unitOfWork.getWork();
    assertEquals(0, work.neu.length);
    assertEquals(0, work.updated.length);
    assertEquals(3, work.deleted.length);
}

function testClearTimes() {
    var set = createSet([
        captionJSON(1, 5, 1),
        captionJSON(5, 99999, 2), 
        captionJSON(-1, -1, 3)]);
    set.clearTimes();
    assertEquals(2, MS_updatedCaptions.length);
    assertEquals(-1, set.caption(0).getStartTime());
    assertEquals(-1, set.caption(0).getEndTime());
    assertEquals(-1, set.caption(1).getStartTime());
    assertEquals(-1, set.caption(1).getEndTime());
}

{% endblock %}
