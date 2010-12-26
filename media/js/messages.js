jQuery.msg = {};

/**
 * Add message to user on top of page, like Django's message framework.
 * Examples:
 * $('.click-me').click(function(){
 *     $.msg.add('Hello, world!');
 *     return false;
 * });
 */
jQuery.extend(jQuery.msg, {
    id: 'messages',
    container: 'div.content',
    delayTime: 3000,
    timer: null,
    get: function(){
        var $ = jQuery;
        var $messages = $('#'+this.id);
        if ( ! $messages.length){
            $messages = $('<div id="'+this.id+'"></div>').prependTo(this.container);
        };
        $messages.show();
        return $messages;
    },
    add: function(text, cls){
        var $ = jQuery;
        var cls = cls || '';
        var $messages = this.get();
        $messages.append('<p class="'+cls+'">'+text+'</p>');
        this.timer && clearTimeout(this.timer);
        this.timer = setTimeout(function(){
            $messages.hide();
        }, this.delayTime);
        return this;
    },
    clean: function(){
        jQuery.msg.get().html('');
        return this;
    }
});
