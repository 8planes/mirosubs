{% extends "jstesting/base_test.html" %}

{% block testscript %}
var testElem;

function setUp() {
    testElem = document.createElement('div');
}

function testSetSize() {
    mirosubs.style.setSize(testElem, 32, 58);
    assertEquals(testElem.style.cssText.replace(/ /gi, ''),
                 "width:32px!important;height:58px!important;");
    mirosubs.style.setWidth(testElem, 33);
    assertEquals(testElem.style.cssText.replace(/ /gi, ''),
                 "width:33px!important;height:58px!important;");
    mirosubs.style.setHeight(testElem, 59);
    assertEquals(testElem.style.cssText.replace(/ /gi, ''),
                 "width:33px!important;height:59px!important;");
}

function testSetPosition() {
    mirosubs.style.setPosition(testElem, new goog.math.Coordinate(32, 58));
    assertEquals(testElem.style.cssText.replace(/ /g, ''),
                 "left:32px!important;top:58px!important;");
    mirosubs.style.setPosition(testElem, null, 59);
    assertEquals(testElem.style.cssText.replace(/ /g, ''),
                 "left:32px!important;top:59px!important;");
    mirosubs.style.setPosition(testElem, 33, null);
    assertEquals(testElem.style.cssText.replace(/ /g, ''),
                 "left:33px!important;top:59px!important;");
    mirosubs.style.setPosition(testElem, new goog.math.Coordinate(34, 60));
    assertEquals(testElem.style.cssText.replace(/ /g, ''),
                 "left:34px!important;top:60px!important;");
}

function testShow() {
    mirosubs.style.showElement(testElem, false);
    assertEquals(testElem.style.cssText.replace(/ /g, ''),
                 'display:none!important;');
    mirosubs.style.showElement(testElem, true);
    assertEquals('', testElem.style.cssText);
}

function testSetVisibility() {
    mirosubs.style.setVisibility(testElem, false);
    assertEquals(testElem.style.cssText.replace(/ /g, ''),
                 'visibility:hidden!important;');
    mirosubs.style.setVisibility(testElem, true);
    assertEquals(testElem.style.cssText.replace(/ /g, ''),
                 'visibility:visible!important;');

}

{% endblock %}