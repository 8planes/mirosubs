{% extends "jstesting/base_test.html" %}
{% block testscript %}

var MS_eventHandler = new goog.events.EventHandler();
var MS_updatedCaptions = [];
var MS_cleared = false;

function MS_updateListener(event) {
    MS_updatedCaptions.push(event.target);
}
function MS_clearListener(event) {
    MS_cleared = true;
}
/* A couple helper functions. */
function captionJSON(start_time, end_time, caption_id, sub_order) {
    return {'start_time' : start_time, 
            'end_time': end_time, 
            'caption_id': caption_id, 
            'sub_order': sub_order};
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
    var captionSet = new mirosubs.subtitle.EditableCaptionSet(
        existingCaptions);
    for (var i = 0; i < captionSet.count(); i++)
        listenToCaption(captionSet.caption(i));
    MS_eventHandler.listen(
        captionSet, 
        mirosubs.subtitle.EditableCaptionSet.EventType.CLEAR_ALL,
        MS_clearListener);
    return captionSet;
};

function setUp() {
    mirosubs.Tracker.getInstance().dontReport();
    mirosubs.SubTracker.getInstance().start(false);
}

function tearDown() {
    MS_eventHandler.removeAll();
    MS_updatedCaptions = [];
    MS_cleared = false;
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
        captionJSON(T0, T1, 1, 1),
        captionJSON(T1, T2, 2, 2), 
        captionJSON(T2, -1, 3, 3)]);
    var minLength = mirosubs.subtitle.EditableCaption.MIN_LENGTH;
    assertMinMaxTimes(set.caption(0), 0, T1 - minLength, 
                      T0 + minLength, T2 - minLength);
    assertMinMaxTimes(set.caption(1), T0 + minLength, T2 - minLength, 
                      T1 + minLength, null);
    assertMinMaxTimes(set.caption(2), T1 + minLength, null, 
                      T2 + minLength, null);
    assertEquals(0, MS_updatedCaptions.length);
}

function testInsertSubAtStart() {
    var minLength = mirosubs.subtitle.EditableCaption.MIN_LENGTH;
    var T0 = minLength / 2, T1 = T0 + minLength, T2 = T1 + minLength;
    var set = createSet([
        captionJSON(T0, T1, 1, 1),
        captionJSON(T1, T2, 2, 2), 
        captionJSON(T2, 99999, 3, 3)]);
    var inserted = set.insertCaption(1);
    assertEquals(0, inserted.getStartTime());
    assertEquals(minLength, inserted.getEndTime());
    assertEquals(minLength, set.caption(1).getStartTime());
    assertNull(inserted.getPreviousCaption());
    assertEquals(set.caption(1), inserted.getNextCaption());
}

function testCreateNewInsertAtStart() {
    var set = createSet([]);
    var caption0 = addNewCaption(set);
    var caption1 = addNewCaption(set);
    var caption2 = addNewCaption(set);
    var inserted = set.insertCaption(caption0.getSubOrder());
    assertTrue(0 < inserted.getSubOrder())
    assertTrue(inserted.getSubOrder() < caption0.getSubOrder())
}

function testInsertSubInMiddle() {
    var minLength = mirosubs.subtitle.EditableCaption.MIN_LENGTH;
    var T0 = minLength / 2, T1 = T0 + minLength, T2 = T1 + minLength;
    var set = createSet([
        captionJSON(T0, T1, 1, 1),
        captionJSON(T1, T2, 2, 2), 
        captionJSON(T2, 99999, 3, 3)]);
    var inserted = set.insertCaption(2);
    assertEquals(set.caption(1), inserted);
    assertEquals(T0, set.caption(0).getStartTime());
    assertEquals(T1, inserted.getStartTime());
    assertEquals(T2, inserted.getEndTime());
    assertEquals(T2, set.caption(2).getStartTime());
}

function testInsertSubInMiddleUnconstrained() {
    var minLength = mirosubs.subtitle.EditableCaption.MIN_LENGTH;
    var T0 = minLength / 2, T1 = T0 + minLength * 3, T2 = T1 + minLength;
    var set = createSet([
        captionJSON(T0, T1, 1, 1),
        captionJSON(T1, T2, 2, 2), 
        captionJSON(T2, 99999, 3, 3)]);
    var inserted = set.insertCaption(1);
    assertEquals(set.caption(0), inserted);
    assertEquals(T0, inserted.getStartTime());
    assertEquals((T0 + T1) / 2, inserted.getEndTime());
    assertEquals((T0 + T1) / 2, set.caption(1).getStartTime());
    assertEquals(T1, set.caption(1).getEndTime());
}

function testInsertSubInMiddleOfUntimed() {
    var set = createSet([]);
    var caption0 = addNewCaption(set);
    var caption1 = addNewCaption(set);
    var caption2 = addNewCaption(set);
    var minLength = mirosubs.subtitle.EditableCaption.MIN_LENGTH;
    var inserted = set.insertCaption(set.caption(1).getSubOrder());
    assertEquals(set.caption(1), inserted);
    assertEquals(set.caption(0), inserted.getPreviousCaption());
    assertEquals(set.caption(2), inserted.getNextCaption());
    assertEquals(-1, inserted.getStartTime());
    assertEquals(-1, inserted.getEndTime());
}

function testInsertSubFirstUntimed() {
    var set = createSet([captionJSON(0.5, 2, 1, 1),
			 captionJSON(2, 3, 2, 2),
			 captionJSON(3, -1, 3, 3),
                         captionJSON(-1, -1, 4, 4)]);
    var inserted = set.insertCaption(set.caption(3).getSubOrder());
    assertEquals(-1, inserted.getStartTime());
    assertEquals(-1, inserted.getEndTime());
}

function testSpacebarHold() {
    var T0 = 1.8, T1 = 5.6, T2 = 9.2;
    var set = createSet([
        captionJSON(T0, T1, 1, 1),
        captionJSON(T1, T2, 2, 2), 
        captionJSON(T2, 99999, 3, 3)]);
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
    var T0 = 1.8, T1 = 5.6, T2 = 8.2;
    var set = createSet([
        captionJSON(T0, T1, 1, 1),
        captionJSON(T1, T2, 2, 2), 
        captionJSON(T2, 99999, 3, 3)]);
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
        captionJSON(T0, T1, 1, 1),
        captionJSON(T1, T2, 2, 2), 
        captionJSON(T2, 99999, 3, 3)]);
    set.clear();
    assertEquals(0, set.count());
    assertTrue(MS_cleared);
}

function testWithNullTimes() {
    var editableCaption = new mirosubs.subtitle.EditableCaption(
        1, 
        { 'subtitle_id': 'a', 
          'text': 'whatever',
          'start_time': null,
          'end_time': null,
          'sub_order': 1.0 });
    assertEquals(-1, editableCaption.getStartTime());
    assertEquals(-1, editableCaption.getEndTime());
}

{% endblock %}
