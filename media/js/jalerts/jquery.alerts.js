// jQuery Alert Dialogs Plugin
//
// Version 1.1
//
// Cory S.N. LaViska
// A Beautiful Site (http://abeautifulsite.net/)
// 14 May 2009
//
// Patched by Alerion:
// You can add extra button to dialog.
//
// License:
// 
// This plugin is dual-licensed under the GNU General Public License and the MIT License and
// is copyright 2008 A Beautiful Site, LLC. 
//
(function($) {
	
	$.alerts = {
		
		// These properties can be read/written by accessing $.alerts.propertyName from your scripts at any time
		
		verticalOffset: -75,                // vertical offset of the dialog from center screen, in pixels
		horizontalOffset: 0,                // horizontal offset of the dialog from center screen, in pixels/
		repositionOnResize: true,           // re-centers the dialog on window resize
		
		defaultOptions: {
			overlayOpacity: .01,                // transparency level of overlay
			overlayColor: '#FFF',               // base color of overlay			
			draggable: true,    // make the dialogs draggable (requires UI Draggables plugin)
			extraButtons: [],
			preventClose: false,
            contentClass: '',
			okButton: {
				name: '&nbsp;OK&nbsp;',
				id: 'popup_ok',
				type: 'OK',
                cls: ''
			},
			cancelButton: {
				name: '&nbsp;Cancel&nbsp;',
				id: 'popup_cancel',
				type: 'CANCEL',
                cls: ''
			},
			dialogClass: null	// if specified, this class will be applied to all dialogs
		},
		
		// Public methods
		
		alert: function(message, title, callback, options) {
			title = title || 'Alert';
			callback = callback || $.noop;
			$.alerts._show(title, message, null, 'alert', callback, options);
		},
		
		confirm: function(message, title, callback, options) {
			title = title || 'Confirm';
			callback = callback || $.noop;
			$.alerts._show(title, message, null, 'confirm', callback, options);
		},
			
		prompt: function(message, value, title, callback, options) {
			title = title || 'Prompt';
			callback = callback || $.noop;
			$.alerts._show(title, message, value, 'prompt', callback, options);
		},
		
		_initButtons: function(buttons, callback, options){
			for (var i=0,len=buttons.length; i<len; i++){
				var bo= buttons[i];
				$('#popup_panel').append('<input type="button" class="'+bo.cls+'" buttonType="'+bo.type+'" value="'+bo.name+'" id="'+bo.id+'" />');
				$("#"+bo.id).click(function(){
					var $prompt_input = $("#popup_prompt");
					
					( ! options.preventClose) && $.alerts.hide();
					if ($prompt_input.length){
						callback($(this).attr('buttonType'), $prompt_input.val(), options);	
					}else{
						callback($(this).attr('buttonType'), options);	
					}
							
				});							
			};			
		},
		
		_show: function(title, msg, value, type, callback, options) {
			options = $.extend({}, $.alerts.defaultOptions, options);
			$.alerts.hide(options);
			$.alerts._overlay('show', options);
			
			$("BODY").append(
			  '<div id="popup_container">' +
			    '<h1 id="popup_title"></h1>' +
			    '<div id="popup_content">' +
			      '<div id="popup_message"></div>' +
				'</div>' +
			  '</div>');
			
			if( options.dialogClass ) $("#popup_container").addClass(options.dialogClass);
			
			// IE6 Fix
			var pos = ($.browser.msie && parseInt($.browser.version) <= 6 ) ? 'absolute' : 'fixed'; 
			
			$("#popup_container").css({
				position: pos,
				zIndex: 99999,
				padding: 0,
				margin: 0
			});
			
			$("#popup_title").text(title);
			$("#popup_content").addClass(options.contentClass || type);
			$("#popup_message").text(msg);
			$("#popup_message").html( $("#popup_message").text().replace(/\n/g, '<br />') );
			
			$("#popup_container").css({
				minWidth: $("#popup_container").outerWidth(),
				maxWidth: $("#popup_container").outerWidth()
			});
			
			$.alerts._reposition();
			$.alerts._maintainPosition(true);
			
			var buttons = [];
			options.okButton && buttons.push(options.okButton);
			options.cancelButton && buttons.push(options.cancelButton);
			buttons = buttons.concat(options.extraButtons);

			switch( type ) {
				case 'alert':
					$("#popup_message").after('<div id="popup_panel"></div>');
					$.alerts._initButtons(buttons, callback, options);
					$("#popup_ok").focus().keypress( function(e) {
						if( e.keyCode == 13 || e.keyCode == 27 ) $("#popup_ok").trigger('click');
					});
				break;
				case 'confirm':
					$("#popup_message").after('<div id="popup_panel"></div>');
					$.alerts._initButtons(buttons, callback, options);
					$("#popup_ok").focus();
					$("#popup_ok, #popup_cancel").keypress( function(e) {
						if( e.keyCode == 13 ) $("#popup_ok").trigger('click');
						if( e.keyCode == 27 ) $("#popup_cancel").trigger('click');
					});
					
				break;
				case 'prompt':
					$("#popup_message").append('<br /><input type="text" size="30" id="popup_prompt" />').after('<div id="popup_panel"></div>');
					$.alerts._initButtons(buttons, callback, options);
					$("#popup_prompt").width($("#popup_message").width());
					$("#popup_prompt, #popup_ok, #popup_cancel").keypress( function(e) {
						if( e.keyCode == 13 ) $("#popup_ok").trigger('click');
						if( e.keyCode == 27 ) $("#popup_cancel").trigger('click');
					});
					if( value ) $("#popup_prompt").val(value);
					$("#popup_prompt").focus().select();
				break;
			}
			
			// Make draggable
			if( options.draggable ) {
				try {
					$("#popup_container").draggable({ handle: $("#popup_title") });
					$("#popup_title").css({ cursor: 'move' });
				} catch(e) { /* requires jQuery UI draggables */ }
			}
		},
		
		hide: function() {
			$("#popup_container").remove();
			$.alerts._overlay('hide');
			$.alerts._maintainPosition(false);
		},
		
		_overlay: function(status, options) {
			switch( status ) {
				case 'show':
					$.alerts._overlay('hide');
					$("BODY").append('<div id="popup_overlay"></div>');
					$("#popup_overlay").css({
						position: 'absolute',
						zIndex: 99998,
						top: '0px',
						left: '0px',
						width: '100%',
						height: $(document).height(),
						background: options.overlayColor,
						opacity: options.overlayOpacity
					});
				break;
				case 'hide':
					$("#popup_overlay").remove();
				break;
			}
		},
		
		_reposition: function() {
			var top = (($(window).height() / 2) - ($("#popup_container").outerHeight() / 2)) + $.alerts.verticalOffset;
			var left = (($(window).width() / 2) - ($("#popup_container").outerWidth() / 2)) + $.alerts.horizontalOffset;
			if( top < 0 ) top = 0;
			if( left < 0 ) left = 0;
			
			// IE6 fix
			if( $.browser.msie && parseInt($.browser.version) <= 6 ) top = top + $(window).scrollTop();
			
			$("#popup_container").css({
				top: top + 'px',
				left: left + 'px'
			});
			$("#popup_overlay").height( $(document).height() );
		},
		
		_maintainPosition: function(status) {
			if( $.alerts.repositionOnResize ) {
				switch(status) {
					case true:
						$(window).bind('resize', $.alerts._reposition);
					break;
					case false:
						$(window).unbind('resize', $.alerts._reposition);
					break;
				}
			}
		}
		
	}
	
	// Shortuct functions
	$.jAlert = function(message, title, callback, options) {
		$.alerts.alert(message, title, callback, options);
	}
	
	$.jConfirm = function(message, title, callback, options) {
		$.alerts.confirm(message, title, callback, options);
	};
		
	$.jPrompt = function(message, value, title, callback, options) {
		$.alerts.prompt(message, value, title, callback, options);
	};
	
})(jQuery);