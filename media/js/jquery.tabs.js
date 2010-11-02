(function($){
    $.fn.tabs = function(options){
        var defaults = {};
        
        var options = $.extend(defaults, options); 

        this.each(function(){
            var $this = $(this);
            
            var $last_active_tab = $($('li.active a', $this).attr('href'));
            $('a', $this).add($('a.link_to_tab')).click(function(){
                var href = $(this).attr('href')
                $last_active_tab.hide();
                $last_active_tab = $(href).show();
                $('li', $this).removeClass('active');
                $('a[href='+href+']', $this).parent('li').addClass('active');
                document.location.hash = href.split('-')[0];
                return false;
            });            
        });
        
        if (document.location.hash){
            var tab_name = document.location.hash.split('-', 1)
            if (tab_name){
                $('a[href='+tab_name+'-tab]').click();
                document.location.href = document.location.href;
            }
        }
        
        return this;        
    };
})(jQuery);  