{% extends "jstesting/base_test.html" %}
{% block testscript %}

/**
 * A map of captionid to count, where count is the number of times we 
 * received a subtitle update event for that captionid.
 */
var MS_subtitleUpdateCounts;
var MS_subtitleUpdateCount;
var MS_addedSubtitles;
var MS_eventHandler;
var MS_videoPlayer;
var MS_unitOfWork;

var MIN_LENGTH = mirosubs.timeline.Subtitle.MIN_UNASSIGNED_LENGTH;
var UNASSIGNED_SPACING = mirosubs.timeline.Subtitle.UNASSIGNED_SPACING;

function MS_subUpdateListener(event) {
    var captionID = event.target.getEditableCaption().getCaptionID() + '';
    if (!MS_subtitleUpdateCounts[captionID])
        MS_subtitleUpdateCounts[captionID] = 1;
    else
        MS_subtitleUpdateCounts[captionID]++;
    MS_subtitleUpdateCount++;
}

function MS_displaySubListener(event) {
    var captionID = event.subtitle.getEditableCaption().getCaptionID() + '';
    MS_addedSubtitles.push(event.subtitle);
    MS_subtitleUpdateCounts[captionID] = 1;
    MS_subtitleUpdateCount++;
    listenToSubtitle(event.subtitle);
}

function MS_clearListener(event) {
    
}

/* helper functions */
function captionJSON(start_time, end_time, caption_id) {
    return {'start_time' : start_time, 
            'end_time': end_time, 
            'caption_id': caption_id};
}

function listenToSubtitle(timelineSub) {
    MS_eventHandler.listen(
        timelineSub,
        mirosubs.timeline.Subtitle.CHANGE,
        MS_subUpdateListener);
}

function sendVideoTimeUpdate(time) {
    MS_videoPlayer.playheadTime = time;
    MS_videoPlayer.dispatchTimeUpdate();
}

function createSet(existingCaptions) {
    var captionSet = new mirosubs.subtitle.EditableCaptionSet(
        existingCaptions, MS_unitOfWork);
    var subtitleSet = new mirosubs.timeline.SubtitleSet(
        captionSet, MS_videoPlayer);
    var subsToDisplay = subtitleSet.getSubsToDisplay();
    for (var i = 0; i < subsToDisplay.length; i++)
        listenToSubtitle(subsToDisplay[i]);
    MS_eventHandler.listen(
        subtitleSet, 
        mirosubs.timeline.SubtitleSet.CLEAR_ALL,
        MS_clearListener);
    MS_eventHandler.listen(
        subtitleSet,
        mirosubs.timeline.SubtitleSet.DISPLAY_NEW,
        MS_displaySubListener);
    return subtitleSet;
};

function assertTimes(sub, start, end) {
    assertEquals(start, sub.getStartTime());
    assertEquals(end, sub.getEndTime());
}

/* setup/teardown */

function setUp() {
    MS_videoPlayer = new mirosubs.testing.StubVideoPlayer();
    MS_videoPlayer.playheadTime = 0;
    MS_unitOfWork = new mirosubs.UnitOfWork();
    MS_eventHandler = new goog.events.EventHandler();
    MS_subtitleUpdateCounts = {};
    MS_subtitleUpdateCount = 0;
    MS_addedSubtitles = [];
}

function testSubsToDisplayLength() {
    var set = createSet([
        captionJSON(0.3, 2.5, 1),
        captionJSON(2.5, -1, 2),
        captionJSON(-1, -1, 3),
        captionJSON(-1, -1, 4)
    ]);
    assertEquals(3, set.getSubsToDisplay().length);
}

function testSubsToDisplay() {
    var T0 = 0.3, T1 = 2.5;
    var set = createSet([
        captionJSON(T0, T1, 1),
        captionJSON(T1, -1, 2),
        captionJSON(-1, -1, 3),
        captionJSON(-1, -1, 4)
    ]);
    var subs = set.getSubsToDisplay();
    assertTimes(subs[0], T0, T1);
    assertTimes(subs[1], T1, T1 + MIN_LENGTH);
    assertTimes(subs[2], 
                T1 + MIN_LENGTH + UNASSIGNED_SPACING, 
                T1 + MIN_LENGTH * 2 + UNASSIGNED_SPACING);
}

function testVideoPlayheadMove() {
    var T0 = 0.3, T1 = 2.5, T2 = 4.6;
    var set = createSet([
        captionJSON(T0, T1, 1),
        captionJSON(T1, -1, 2),
        captionJSON(-1, -1, 3),
        captionJSON(-1, -1, 4)
    ]);
    var subs = set.getSubsToDisplay();
    sendVideoTimeUpdate(0.2);
    sendVideoTimeUpdate(0.3);
    sendVideoTimeUpdate(2.6);
    assertEquals(0, MS_subtitleUpdateCount);
    sendVideoTimeUpdate(T2);
    assertEquals(2, MS_subtitleUpdateCount);
    assertEquals(1, MS_subtitleUpdateCounts['2']);
    assertEquals(1, MS_subtitleUpdateCounts['3']);
    assertTimes(subs[1], T1, T2);
    assertTimes(subs[2], 
                T2 + UNASSIGNED_SPACING,
                T2 + UNASSIGNED_SPACING + MIN_LENGTH);
    // now move playhead back
    sendVideoTimeUpdate(0.2);
    assertEquals(4, MS_subtitleUpdateCount);    
    assertTimes(subs[1], T1, T1 + MIN_LENGTH);
    assertTimes(subs[2], 
                T1 + MIN_LENGTH + UNASSIGNED_SPACING, 
                T1 + MIN_LENGTH * 2 + UNASSIGNED_SPACING);
}

function testAssignTime() {
    var T0 = 0.3, T1 = 2.5, T2 = 4.6, T3 = 7;
    var set = createSet([
        captionJSON(T0, T1, 1),
        captionJSON(T1, -1, 2),
        captionJSON(-1, -1, 3),
        captionJSON(-1, -1, 4)
    ]);
    var subs = set.getSubsToDisplay();
    sendVideoTimeUpdate(T2);
    subs[2].getEditableCaption().setStartTime(T2);
    assertEquals(1, MS_subtitleUpdateCounts['4']);
    assertEquals(5, MS_subtitleUpdateCount);
    assertEquals(1, MS_addedSubtitles.length);
    var newSub = MS_addedSubtitles[0];
    assertTimes(subs[1], T1, T2);
    assertTimes(subs[2], T2, T2 + MIN_LENGTH);
    assertTimes(newSub, 
                T2 + MIN_LENGTH + UNASSIGNED_SPACING,
                T2 + MIN_LENGTH * 2 + UNASSIGNED_SPACING);
    sendVideoTimeUpdate(T3);
    assertEquals(2, MS_subtitleUpdateCounts['4']);
    assertEquals(7, MS_subtitleUpdateCount);
    assertTimes(subs[2], T2, T3);
    assertTimes(newSub,
                T3 + UNASSIGNED_SPACING,
                T3 + UNASSIGNED_SPACING + MIN_LENGTH);
}

function testStartOut() {
    var set = createSet([
        captionJSON(-1, -1, 1),
        captionJSON(-1, -1, 2),
        captionJSON(-1, -1, 3),
        captionJSON(-1, -1, 4)
    ]);
    var subs = set.getSubsToDisplay();
    assertEquals(1, subs.length);
    assertTimes(subs[0], UNASSIGNED_SPACING, 
               UNASSIGNED_SPACING + MIN_LENGTH);
    var T0 = 3;
    sendVideoTimeUpdate(T0);
    assertEquals(1, MS_subtitleUpdateCount);
    assertTimes(subs[0], T0 + UNASSIGNED_SPACING,
                T0 + UNASSIGNED_SPACING + MIN_LENGTH);
    subs[0].getEditableCaption().setStartTime(T0);
    assertEquals(2, MS_subtitleUpdateCounts['1']);
    assertEquals(1, MS_addedSubtitles.length);
    var T1= 5;
    sendVideoTimeUpdate(T1);
    assertTimes(subs[0], T0, T1);
    assertTimes(MS_addedSubtitles[0], 
                T1 + UNASSIGNED_SPACING,
                T1 + UNASSIGNED_SPACING + MIN_LENGTH);
}

function testStartWithLoneUnsynced() {
    var T0 = 8, T1 = 10;
    var set = createSet([
        captionJSON(0.5, 4, 1),
        captionJSON(4.5, T0, 2),
        captionJSON(-1, -1, 3),
        captionJSON(-1, -1, 4)
    ]);
    var subs = set.getSubsToDisplay();
    assertEquals(3, subs.length);
    assertTimes(subs[2],
                T0 + UNASSIGNED_SPACING,
                T0 + UNASSIGNED_SPACING + MIN_LENGTH);
    sendVideoTimeUpdate(T1);
    assertEquals(1, MS_subtitleUpdateCount);
    assertTimes(subs[2],
                T1 + UNASSIGNED_SPACING,
                T1 + UNASSIGNED_SPACING + MIN_LENGTH);
}

{% endblock %}