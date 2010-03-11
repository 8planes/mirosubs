{% extends "jstesting/base_test.html" %}
{% block testcontrols %}
<span id="syncpanel"></span>
{% endblock %}
{% block testscript %}

var MS_syncPanel = null;
var MS_unitOfWork = null;
var MS_editableCaptions = [];
var MS_videoPlayer = null;
var MS_captionManager = null;
var MS_space = goog.events.KeyCodes.SPACE;

// helper methods to avoid typing too much

function makeEditableCaption(unitOfWork, start, end, id) {
    var jsonCaption = {'start_time' : start, 
                       'end_time': end, 
                       'caption_id': id};
    return new mirosubs.subtitle.EditableCaption(unitOfWork, jsonCaption);
}

function spacePress() {
    goog.testing.events.fireKeySequence(window, MS_space);    
}

function spaceDown() {
    mirosubs.testing.events.fireKeyDown(window, MS_space);
}

function spaceUp() {
    mirosubs.testing.events.fireKeyUp(window, MS_space);
}

function assertSubStart(subIndex, start) {
    assertEquals(start, MS_editableCaptions[subIndex].getStartTime());
}

function assertSubEnd(subIndex, end) {
    assertEquals(end, MS_editableCaptions[subIndex].getEndTime());
}

// the tests

function setUp() {
    MS_unitOfWork = new mirosubs.UnitOfWork();
    MS_videoPlayer = new mirosubs.testing.StubVideoPlayer();
    MS_editableCaptions = 
        [makeEditableCaption(MS_unitOfWork, -1, -1, 1),
         makeEditableCaption(MS_unitOfWork, -1, -1, 2),
         makeEditableCaption(MS_unitOfWork, -1, -1, 3)];
    MS_captionManager = new mirosubs.CaptionManager(MS_videoPlayer.getPlayheadFn());
    MS_syncPanel = new mirosubs.subtitle.SyncPanel(MS_editableCaptions, 
                                                   MS_videoPlayer,
                                                   MS_captionManager);
    MS_syncPanel.render(goog.dom.$('syncpanel'));
    MS_videoPlayer.play();
}

function tearDown() {
    MS_syncPanel.dispose();
    MS_captionManager.dispose();
    MS_unitOfWork.dispose();
}

function testAssignSubtitles() {
    MS_videoPlayer.playheadTime = 0.3;
    spacePress();
    MS_videoPlayer.playheadTime = 1.2;
    spacePress();
    assertSubStart(0, 0.3);
    assertSubEnd(0, 1.2);
    assertSubStart(1, 1.2);
    assertTrue(MS_editableCaptions[1].getEndTime() > 3600);
}

function testMoveFirstSubtitle() {
    MS_videoPlayer.playheadTime = 0.8;
    spacePress();
    MS_videoPlayer.playheadTime = 1.2;
    spacePress();
    MS_videoPlayer.playheadTime = 0.3;
    spacePress();
    assertSubStart(0, 0.3);
    assertSubEnd(0, 1.2);
    assertSubStart(1, 1.2);
    assertTrue(MS_editableCaptions[1].getEndTime() > 3600);
}

function testAssignAllSubtitles() {
    MS_videoPlayer.playheadTime = 0.3;
    spacePress();
    MS_videoPlayer.playheadTime = 1.2;
    spacePress();
    MS_videoPlayer.playheadTime = 2.0;
    spacePress();
    MS_videoPlayer.playheadTime = 3.0;
    spacePress();
    assertSubStart(0, 0.3);
    assertSubEnd(0, 1.2);
    assertSubStart(1, 1.2);
    assertSubEnd(1, 2.0);
    assertSubStart(2, 2.0);
    assertSubEnd(2, 3.0);
}

function testMoveMiddleSubtitle() {
    MS_videoPlayer.playheadTime = 0.8;
    spacePress();
    MS_videoPlayer.playheadTime = 3.0;
    spacePress();
    MS_videoPlayer.playheadTime = 2.0;
    spacePress();
    assertSubStart(0, 0.8);
    assertSubEnd(0, 2.0);
    assertSubStart(1, 2.0);    
}

function testClearOneSubtitle() {
    MS_videoPlayer.playheadTime = 0.3;
    spacePress();
    MS_videoPlayer.playheadTime = 1.2;
    spacePress();
    MS_videoPlayer.playheadTime = 0.8;
    spaceDown();
    MS_videoPlayer.playheadTime = 1.3;
    spaceUp();
    assertSubStart(0, 0.3);
    assertSubEnd(0, 1.3);
    assertSubStart(1, 1.3);
}

{% endblock %}