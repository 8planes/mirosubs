{% extends "jstesting/base_test.html" %}
{% block testcontrols %}
<span id="syncpanel"></span>
{% endblock %}
{% block testscript %}

var MS_syncPanel = null;
var MS_unitOfWork = null;
var MS_captionSet = [];
var MS_videoPlayer = null;
var MS_captionManager = null;
var MS_space = goog.events.KeyCodes.SPACE;

// helper methods to avoid typing too much

function captionJSON(start, end, id) {
    return {'start_time' : start, 
            'end_time': end, 
            'caption_id': id};
}

function spacePress() {
    goog.testing.events.fireKeySequence(document, MS_space);
}

function spaceDown() {
    mirosubs.testing.events.fireKeyDown(document, MS_space);
}

function spaceUp() {
    mirosubs.testing.events.fireKeyUp(document, MS_space);
}

function assertTimes(subIndex, start, end) {
    assertEquals(start, MS_captionSet.caption(subIndex).getStartTime());
    if (end == null)
        assertTrue(MS_captionSet.caption(subIndex).getEndTime() > 9999);
    else
        assertEquals(end, MS_captionSet.caption(subIndex).getEndTime());
}

function setUpSubs(opt_subs) {
    MS_unitOfWork = new mirosubs.UnitOfWork();
    MS_videoPlayer = new mirosubs.testing.StubVideoPlayer();
    subs = opt_subs || [captionJSON(-1, -1, 1),
                        captionJSON(-1, -1, 2),
                        captionJSON(-1, -1, 3)];
    MS_captionSet = 
        new mirosubs.subtitle.EditableCaptionSet(
            MS_unitOfWork, subs);
    MS_captionManager = new mirosubs.CaptionManager(MS_videoPlayer.getPlayheadFn());
    MS_syncPanel = new mirosubs.subtitle.SyncPanel(MS_captionSet, 
                                                   MS_videoPlayer,
                                                   null,
                                                   MS_captionManager);
    MS_syncPanel.render(goog.dom.$('syncpanel'));
    MS_videoPlayer.play();
}

// the tests

function tearDown() {
    MS_syncPanel.dispose();
    MS_captionManager.dispose();
    MS_unitOfWork.dispose();
}

function testAssignSubtitles() {
    setUpSubs();
    MS_videoPlayer.playheadTime = 0.3;
    spacePress();
    MS_videoPlayer.playheadTime = 5.4;
    spacePress();
    assertTimes(0, 0.3, 5.4);
    assertTimes(1, 5.4, null);
}

function testMoveFirstSubtitle() {
    setUpSubs();
    MS_videoPlayer.playheadTime = 0.8;
    spacePress();
    MS_videoPlayer.playheadTime = 5.2;
    spacePress();
    MS_videoPlayer.playheadTime = 0.3;
    spacePress();
    assertTimes(0, 0.3, 5.2);
    assertTimes(1, 5.2, null);
}

function testAssignAllSubtitles() {
    setUpSubs();
    MS_videoPlayer.playheadTime = 0.3;
    spacePress();
    MS_videoPlayer.playheadTime = 5.2;
    spacePress();
    MS_videoPlayer.playheadTime = 8.0;
    spacePress();
    MS_videoPlayer.playheadTime = 10.0;
    spacePress();
    assertTimes(0, 0.3, 5.2);
    assertTimes(1, 5.2, 8.0);
    assertTimes(2, 8.0, 10.0);
}

function testMoveMiddleSubtitle() {
    setUpSubs();
    MS_videoPlayer.playheadTime = 0.8;
    spacePress();
    MS_videoPlayer.playheadTime = 9.0;
    spacePress();
    MS_videoPlayer.playheadTime = 6.0;
    spacePress();
    assertTimes(0, 0.8, 6.0);
    assertTimes(1, 6.0, null);
}

function testClearOneSubtitle() {
    setUpSubs();
    MS_videoPlayer.playheadTime = 0.3;
    spacePress();
    MS_videoPlayer.playheadTime = 5.2;
    spacePress();
    MS_videoPlayer.playheadTime = 0.8;
    spaceDown();
    MS_videoPlayer.playheadTime = 6.3;
    spaceUp();
    assertTimes(0, 0.3, 6.3);
    assertTimes(1, 6.3, null);
}

function testMoveFirstSubtitleByHolding() {
    setUpSubs([captionJSON(5, 10, 1),
               captionJSON(10, 15, 2),
               captionJSON(15, 20, 3)]);
    MS_videoPlayer.playheadTime = 2;
    spaceDown();
    MS_videoPlayer.playheadTime = 7;
    spaceUp();
    assertTimes(0, 7, 10);
}

function testMoveFirstTwoSubs() {
    setUpSubs([captionJSON(5, 10, 1),
               captionJSON(10, 15, 2),
               captionJSON(15, 20, 3)]);
    var minLength = mirosubs.subtitle.EditableCaption.MIN_LENGTH;
    MS_videoPlayer.playheadTime = 2;
    spaceDown();
    MS_videoPlayer.playheadTime = 17;
    spaceUp();
    assertTimes(0, 17, 17 + minLength);
    assertTimes(1, 17 + minLength, 17 + minLength * 2);
    assertTimes(2, 17 + minLength * 2, Math.max(17 + minLength * 3, 20));
}

function testMoveLastSub() {
    setUpSubs([captionJSON(5, 10, 1),
               captionJSON(10, 15, 2),
               captionJSON(15, 20, 3)]);
    MS_videoPlayer.playheadTime = 19;
    spaceDown();
    MS_videoPlayer.playheadTime = 22;
    spaceUp();
    assertTimes(2, 15, 22);
}

function testMoveEndOfFirstSubWithSpace() {
    // here we have spaces between subs (from using timeline)
    // and we press space in the middle of the first sub, releasing 
    // it between the first and second.
    setUpSubs([captionJSON(5, 10, 1),
               captionJSON(15, 20, 2),
               captionJSON(25, 30, 3)]);
    MS_videoPlayer.playheadTime = 7;
    spaceDown();
    MS_videoPlayer.playheadTime = 12;
    spaceUp();
    assertTimes(0, 5, 12);
    assertTimes(1, 15, 20);
}

function testMoveStartOfSecondSubWithSpace0() {
    // here we have spaces between subs (from using timeline)
    // and we press space between the first and second, releasing 
    // in the middle of the second.
    setUpSubs([captionJSON(5, 10, 1),
               captionJSON(15, 20, 2),
               captionJSON(25, 30, 3)]);
    MS_videoPlayer.playheadTime = 13;
    spaceDown();
    MS_videoPlayer.playheadTime = 17;
    spaceUp();
    assertTimes(0, 5, 10);
    assertTimes(1, 17, 20);
    assertTimes(2, 25, 30);
}

function testMoveStartOfSecondSubWithSpace1() {
    // here we have spaces between subs (from using timeline)
    // and we press space between the first and second, releasing 
    // between the first and second also.
    setUpSubs([captionJSON(5, 10, 1),
               captionJSON(15, 20, 2),
               captionJSON(25, 30, 3)]);
    MS_videoPlayer.playheadTime = 13;
    spaceDown();
    MS_videoPlayer.playheadTime = 14;
    spaceUp();
    assertTimes(0, 5, 10);
    assertTimes(1, 14, 20);
    assertTimes(2, 25, 30);
}


function testClearFirstTwoWithSpace() {
    // here we have spaces between subs (from using timeline)
    // and we press space before the first, releasing 
    // after the second.
    setUpSubs([captionJSON(5, 10, 1),
               captionJSON(15, 20, 2),
               captionJSON(30, 35, 3)]);
    var minLength = mirosubs.subtitle.EditableCaption.MIN_LENGTH;
    MS_videoPlayer.playheadTime = 3;
    spaceDown();
    MS_videoPlayer.playheadTime = 22;
    spaceUp();
    assertTimes(0, 22, 22 + minLength);
    assertTimes(1, 22 + minLength, 22 + minLength * 2);
    assertTimes(2, 30, 35);
}

function testClearMiddleWithSpace() {
    // here we have spaces between subs (from using timeline)
    // and we press space before the second, releasing 
    // after the second.
    setUpSubs([captionJSON(5, 10, 1),
               captionJSON(15, 20, 2),
               captionJSON(30, 35, 3)]);
    var minLength = mirosubs.subtitle.EditableCaption.MIN_LENGTH;
    MS_videoPlayer.playheadTime = 13;
    spaceDown();
    MS_videoPlayer.playheadTime = 22;
    spaceUp();
    assertTimes(0, 5, 10);
    assertTimes(1, 22, 22 + minLength);
    assertTimes(2, 30, 35);
}


{% endblock %}