{% extends "jstesting/base_test.html" %}
{% block testscript %}

var MS_captionManager = null;
var MS_videoPlayer = null;
var MS_editableCaptionSet = null;

/* stub caption listener machinery for testing */

var MS_dispatchedCaptions = [];
function MS_captionListener(event) {
    MS_dispatchedCaptions.push(event.caption);
}

/* a few helper methods to avoid typing too much */

function captionJSON(startTime, endTime, captionID, subOrder) {
    return {'start_time' : startTime,
	    'end_time': endTime,
	    'subtitle_id': captionID,
            'sub_order': subOrder};
}
function sendEvents(playheadTime) {
    MS_videoPlayer.playheadTime = playheadTime;
    MS_videoPlayer.dispatchTimeUpdate();
}

function addNewCaption(startTime, endTime) {
    var caption = MS_editableCaptionSet.addNewCaption();
    caption.setStartTime(startTime);
    caption.setEndTime(endTime);
    return caption;
}

/* the tests */

function setUp() {
    mirosubs.REPORT_ANALYTICS = false;
    mirosubs.SubTracker.getInstance().start(false);
}

function setUpForInitialCaptions(captions) {
    var uw = new mirosubs.UnitOfWork();
    MS_editableCaptionSet =
	     new mirosubs.subtitle.EditableCaptionSet(captions, uw);
    MS_dispatchedCaptions = [];
    MS_videoPlayer = new mirosubs.testing.StubVideoPlayer();
    MS_captionManager = new mirosubs.CaptionManager(
	MS_videoPlayer, MS_editableCaptionSet);
    MS_captionManager.addEventListener(
	mirosubs.CaptionManager.CAPTION, MS_captionListener);
}

function tearDown() {
    MS_captionManager.dispose();
    MS_videoPlayer.dispose();
    MS_editableCaptionSet.dispose();
}

function testOneCaption() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1)]);
    sendEvents(0.4);
    assertEquals(0, MS_dispatchedCaptions.length);
    sendEvents(0.5);
    sendEvents(0.6);
    assertEquals(1, MS_dispatchedCaptions.length);
    assertEquals(1, MS_dispatchedCaptions[0].getCaptionID());
}

function testTwoUpdates() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1)]);
    sendEvents(0.2);
    sendEvents(0.4);
    assertEquals(0, MS_dispatchedCaptions.length);
    sendEvents(0.6);
    sendEvents(0.8);
    assertEquals(1, MS_dispatchedCaptions.length);
}

function testRewind() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1)]);
    sendEvents(0.3);
    sendEvents(0.6);
    sendEvents(0.4);
    assertEquals(2, MS_dispatchedCaptions.length);
    assertNull(MS_dispatchedCaptions[1]);
}

function testRewind2() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1), 
                             captionJSON(2, 3, 2, 2), 
                             captionJSON(3, 4, 3, 3)]);
    sendEvents(0.3);
    sendEvents(1.3);
    sendEvents(2.3);
    assertEquals(2, MS_dispatchedCaptions.length);
    sendEvents(1.3);
    assertEquals(3, MS_dispatchedCaptions.length);
    sendEvents(0.3);
    assertEquals(4, MS_dispatchedCaptions.length);
    assertNull(MS_dispatchedCaptions[3]);
}

function testProgressToNextCaptionAdjacent() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1), 
                             captionJSON(2, 3, 2, 2)]);
    sendEvents(0.3);
    sendEvents(1);
    sendEvents(2.5);
    assertEquals(2, MS_dispatchedCaptions.length);
    assertEquals(1, MS_dispatchedCaptions[0].getCaptionID());
    assertEquals(2, MS_dispatchedCaptions[1].getCaptionID());
}

function testProgressToNextCaptionDisjoint() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1), 
                             captionJSON(2.5, 3, 2, 2)]);
    sendEvents(0.3);
    sendEvents(1);
    sendEvents(2.2);
    sendEvents(2.6);
    sendEvents(3.1);
    assertEquals(4, MS_dispatchedCaptions.length);
    assertEquals(1, MS_dispatchedCaptions[0].getCaptionID());
    assertNull(MS_dispatchedCaptions[1]);
    assertEquals(2, MS_dispatchedCaptions[2].getCaptionID());
    assertNull(MS_dispatchedCaptions[3]);
}

function testInsertCaptionAfter() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1)]);
    sendEvents(0.3);
    sendEvents(1.3);
    sendEvents(2.1);
    var c = addNewCaption(2.2, 3.4);
    sendEvents(2.4);
    assertEquals(3, MS_dispatchedCaptions.length);
    assertEquals(c, MS_dispatchedCaptions[2]);
}

function testInsertCaptionBefore() {
    setUpForInitialCaptions([captionJSON(1, 5, 1)]);
    sendEvents(0.5);
    sendEvents(4);
    var c = addNewCaption(3, 6);
    sendEvents(4.2);
    assertEquals(2, MS_dispatchedCaptions.length);
    assertEquals(c, MS_dispatchedCaptions[1]);
}

function testInsertCaptionUnderCurrentPlayheadTime() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1)]);
    sendEvents(0.3);
    sendEvents(1.3);
    sendEvents(2.2);
    var c = addNewCaption(2.1, 3.4);
    sendEvents(2.2);
    assertEquals(3, MS_dispatchedCaptions.length);
    assertEquals(c, MS_dispatchedCaptions[2]);
}

function testAlterCurrentCaptionTime() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1)]);
    var c = MS_editableCaptionSet.caption(0);
    sendEvents(0.3);
    sendEvents(1.3);
    c.setEndTime(3);
    sendEvents(2.2);
    c.setStartTime(2.5);
    sendEvents(2.3);
    assertEquals(2, MS_dispatchedCaptions.length);
    assertNull(MS_dispatchedCaptions[1]);
}

function testProgressToEnd() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1),
			     captionJSON(2, 3, 2, 2),
			     captionJSON(3, 4, 3, 3)]);
    sendEvents(0.3);
    sendEvents(1.3);
    sendEvents(2.3);
    sendEvents(3.3);
    sendEvents(4.3);
    assertEquals(4, MS_dispatchedCaptions.length);
    assertNull(MS_dispatchedCaptions[3]);
}

function testProgressToOpenEnd() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1),
			     captionJSON(2, 3, 2, 2),
			     captionJSON(3, -1, 3, 3)]);
    sendEvents(0.3);
    sendEvents(1.3);
    sendEvents(2.3);
    sendEvents(3.3);
    sendEvents(4.3);
    assertEquals(3, MS_dispatchedCaptions.length);
    assertEquals(3, MS_dispatchedCaptions[2].getCaptionID());
}

function testProgressToOpenEndPlusOne() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1),
			     captionJSON(2, 3, 2, 2),
			     captionJSON(3, -1, 3, 3),
                             captionJSON(-1, -1, 4, 4)]);
    sendEvents(0.3);
    sendEvents(1.3);
    sendEvents(2.3);
    sendEvents(3.3);
    sendEvents(4.3);
    assertEquals(3, MS_dispatchedCaptions.length);
    assertEquals(3, MS_dispatchedCaptions[2].getCaptionID());
}


function testProgressToEndTwice() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1), 
                             captionJSON(2, 3, 2, 2), 
                             captionJSON(3, 4, 3, 3)]);
    sendEvents(0.3);
    sendEvents(1.3);
    sendEvents(2.3);
    sendEvents(3.3);
    sendEvents(4.3);
    sendEvents(4.5);
    assertEquals(4, MS_dispatchedCaptions.length);
    assertNull(MS_dispatchedCaptions[3]);
}

function testClearTimes() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1), 
                             captionJSON(2, 3, 2, 2), 
                             captionJSON(3, 4, 3, 3)]);
    sendEvents(0.3);
    sendEvents(1.3);
    sendEvents(2.3);
    assertEquals(2, MS_dispatchedCaptions.length);

    MS_editableCaptionSet.clearTimes();

    assertEquals(3, MS_dispatchedCaptions.length);
    assertNull(MS_dispatchedCaptions[2]);
}

function testInsertSub() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1), 
                             captionJSON(2, 3, 2, 2), 
                             captionJSON(3, 4, 3, 3)]);
    sendEvents(2.1);
    assertEquals(1, MS_dispatchedCaptions.length);
    // inserting new caption under current playhead time
    var inserted = MS_editableCaptionSet.insertCaption(
        MS_editableCaptionSet.caption(1).getSubOrder());
    assertEquals(2, MS_dispatchedCaptions.length);
    assertEquals(2, MS_dispatchedCaptions[0].getCaptionID());
    assertEquals(inserted.getCaptionID(), 
                 MS_dispatchedCaptions[1].getCaptionID());
    sendEvents(3.1);
    assertEquals(3, MS_dispatchedCaptions.length);
    assertEquals(3, MS_dispatchedCaptions[2].getCaptionID());
}

function testInsertNoTime() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1),
			     captionJSON(2, 3, 2, 2),
			     captionJSON(3, -1, 3, 3),
                             captionJSON(-1, -1, 4, 4)]);
    sendEvents(4.3);
    assertEquals(1, MS_dispatchedCaptions.length);
    assertEquals(3, MS_dispatchedCaptions[0].getCaptionID());
    var inserted = MS_editableCaptionSet.insertCaption(
        MS_editableCaptionSet.caption(3).getSubOrder());
    assertEquals(1, MS_dispatchedCaptions.length);
    sendEvents(4.4)
    assertEquals(1, MS_dispatchedCaptions.length);
}

function testDeleteSub() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1), 
                             captionJSON(2, 3, 2, 2), 
                             captionJSON(3, 4, 3, 3)]);
    sendEvents(2.1);
    assertEquals(1, MS_dispatchedCaptions.length);
    MS_editableCaptionSet.deleteCaption(
        MS_editableCaptionSet.caption(1));
    assertEquals(2, MS_dispatchedCaptions.length);
    assertNull(MS_dispatchedCaptions[1]);
}

function testDeleteNonCurrentSub() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1), 
                             captionJSON(2, 3, 2, 2), 
                             captionJSON(3, 4, 3, 3)]);
    sendEvents(3.1);
    assertEquals(1, MS_dispatchedCaptions.length);
    MS_editableCaptionSet.deleteCaption(
        MS_editableCaptionSet.caption(1));
    assertEquals(1, MS_dispatchedCaptions.length);
}

function testDeleteSubNoTime() {
    setUpForInitialCaptions([captionJSON(0.5, 2, 1, 1),
			     captionJSON(2, 3, 2, 2),
			     captionJSON(3, -1, 3, 3),
                             captionJSON(-1, -1, 4, 4)]);
    sendEvents(4.3);
    MS_editableCaptionSet.deleteCaption(
        MS_editableCaptionSet.caption(3));
    assertEquals(1, MS_dispatchedCaptions.length);
}

function testNeedsSync() {
    // function captionJSON(startTime, endTime, captionID, subOrder) {
    setUpForInitialCaptions([
        captionJSON(0.5, 2, 1, 1),
		captionJSON(2, 3, 2, 2)
        ]);
 
    assertFalse(MS_editableCaptionSet.needsSync() );

    setUpForInitialCaptions([
        captionJSON(0.5, 2, 1, 1),
		captionJSON(-1, 3, 2, 2)
        ]);
    assertTrue(MS_editableCaptionSet.needsSync());

    setUpForInitialCaptions([
        captionJSON(0.5, 2, 1, 1),
		captionJSON(1, -1, 2, 2),
        captionJSON(4, 5, 2, 2)
        ]);
    assertTrue(MS_editableCaptionSet.needsSync());

    setUpForInitialCaptions([
        captionJSON(0.5, 2, 1, 1),
        captionJSON(2.5, 3.5, 1, 1),
		captionJSON(4, -1, 2, 2)
        ]);
    // the last subtile can have a end time undefined
    // and not need syncing (this means that it will
    // go until the end of video
    assertFalse(MS_editableCaptionSet.needsSync());
}


{% endblock %}
