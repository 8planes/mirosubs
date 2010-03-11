/**
 * @fileoverview Event Simulation.
 *
 * Utilities to complement those in goog.testing.events for testing 
 * events at the Closure level. In particular, provides fireKeyDown 
 * and fireKeyUp functions, which are not provided by 
 * goog.testing.events.
 */

goog.provide('mirosubs.testing.events');

/**
 * Simulates a keydown event.
 *
 * @param {EventTarget} target The target for the event.
 * @param {number} keyCode The keycode of the key pressed.
 * @return {boolean} The returnValue of the event: false 
 *     if preventDefault() was called, true otherwise.
 */
mirosubs.testing.events.fireKeyDown = function(target, keyCode) {
    var keydown =
    new goog.testing.events.Event(goog.events.EventType.KEYDOWN, 
                                  target);
    keydown.keyCode = keyCode;
    return goog.testing.events.fireBrowserEvent(keydown);
};

/**
 * Simulates a keyup event.
 *
 * @param {EventTarget} target The target for the event.
 * @param {number} keyCode The keycode of the key pressed.
 * @return {boolean} The returnValue of the event: false 
 *     if preventDefault() was called, true otherwise.
 */
mirosubs.testing.events.fireKeyUp = function(target, keyCode) {
    var keyup =
    new goog.testing.events.Event(goog.events.EventType.KEYUP, 
                                  target);
    keyup.keyCode = keyCode;
    return goog.testing.events.fireBrowserEvent(keyup);
};