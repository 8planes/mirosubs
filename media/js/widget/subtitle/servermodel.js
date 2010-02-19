/**
 * @fileoverview Definition of the the mirosubs.subtitle.ServerModel 
 *     interface
 *
 */

goog.provide('mirosubs.subtitle.ServerModel');

/**
 * Interface for interaction with server during subtitling work.
 * @interface
 */
mirosubs.subtitle.ServerModel = function() {};

/**
 * Initializes this ServerModel with a UnitOfWork. The server model then 
 * proceeds to save periodically (or not) using the work recorded by the 
 * UnitOfWork. This method can only be called once.
 * @param {mirosubs.UnitOfWork} unitOfWork
 */
mirosubs.subtitle.ServerModel.prototype.init = function(unitOfWork) {};

/**
 * Announces to the server that subtitling is finished. Also frees timers, 
 * etc. This method can only be called after init, and can only be called 
 * once.
 * @param {function()} callback
 */
mirosubs.subtitle.ServerModel.prototype.finish = function(callback) {};

/**
 * Instances implementing this interface must extend goog.Disposable
 */
mirosubs.subtitle.ServerModel.prototype.dispose = function() {};

mirosubs.subtitle.ServerModel.prototype.getEmbedCode = function() {};

mirosubs.subtitle.ServerModel.prototype.currentUsername = function() {};

mirosubs.subtitle.ServerModel.prototype.logIn = function() {};

mirosubs.subtitle.ServerModel.prototype.logOut = function() {};