/*
 * Jquery Ajax Paginator Plugin
 * @requires jQuery 1.3 or later
 * @requires jQuery Address Plugin v1.4 http://www.asual.com/jquery/address/
 * 
 */
(function($){
/*
 * Example of usage:
  
    $('.ajax-pagination').ajaxPaginator({
        container: $('.watch-page-content'),
        onPageChange: function(page, callback){
            VideosApi.load_watch_page(page, function(data){
                this.options.container.html(data.content || '');
                callback.call(this, data);
            }, this);
        },
    });
    
 *  For more information see options.
 */

 $.widget("unisub.ajaxPaginator", {
     prevLink: null,
     nextLink: null,
     fromValueNode: null,
     toValueNode: null,
     totalValueNode: null,
     pageInfoNode: null,
     loadingIndicator: null,
     container: null,
     
     page: 1, //current page
     pages: null,  //total number of pages. Can be empty on page load, when we don't know have many pages have
     timeoutId: null, //callback timer ID
     
     options: {
         pages: null,
         prevLink: '.pag_prev',
         nextLink: '.pag_next',
         pageInfoNode: '.page-info',
         loadingIndicator: '.loading-indicator',
         fromValueNode: '.from-value',
         toValueNode: '.to-value',
         totalValueNode: '.total-value',
         container: null,
         
         //null - for scrolling to container, false - not scroll,
         //'top' - to page top, or some other jQuery node
         scrollTo: 'top', 
         scrollSpeed: 200,
         scrollOffset: -10,
         
         onPageChange: function(page, callback, parameters){
             /*
              * This method get page number and should load/change page content.
              * Callback should be executed with changed metadata in format:
              * {
              *     total: <int>,
              *     pages: <int>,
              *     from: <int>,
              *     to: <int>
              * }
              */
         }
     },
     
     _create: function() {
         var elements = ['prevLink', 'nextLink', 'fromValueNode', 'toValueNode', 
            'pageInfoNode', 'totalValueNode', 'loadingIndicator'];
         
         for (var i=elements.length; i--;){
             var name = elements[i];
             if (typeof this.options[name] == 'string'){
                 this[name] = $(this.options[name], this.element);
             }else{
                 this[name] = this.options[name];
             }                     
         };
         //I just hate this.options, so like add them to this
         this.pages = this.options.pages;
         this.onPageChange = this.options.onPageChange;
         this.container = this.options.container;
     },
     _init: function(){
         var page = $.address.parameter('page')-0;
         page = page || this.page;
         this.setPage(page, true);
         
         var that = this;
         
         this.prevLink.click(function(){
             that._onPrevClick.apply(that, arguments);
             return false;
         });
         
         this.nextLink.click(function(){
             that._onNextClick.apply(that, arguments);
             return false;
         });
         
         $.address.change(function(){
             that._onAdressChange.apply(that, arguments);
         });
     },
     _onAdressChange: function(event){
         var page = event.parameters.page-0;
         if (page !== this.page){
             this.setPage(page || 1, true);
         }
     },
     _onNextClick: function(){
         if (this.pages && this.page < this.pages){
             this.setPage(this.page + 1);
         }
     },
     _onPrevClick: function(){
         if (this.page > 1){
            this.setPage(this.page - 1);
         }
     },
     _createDelegate: function(func, args, scope){
         return function(){
             callArgs = Array.prototype.slice.call(arguments, 0);
             callArgs = callArgs.concat(args);
             return func.apply(scope || window, callArgs);
         }
     },
     updateContent: function(data){
        var $c = this.container;
        
        //fix Chrome page jumping
        $.browser.webkit && $c.css('height', $c.height()+'px');
        
        $c.html(data.content || '');
        
        //fix Chrome page jumping
        if ($.browser.webkit) {
            setTimeout(function(){
                $c.css('height', $c.children().height()+'px');
            }, 1);
        };
     },
     scrollAfterUpdate: function(data, likeReload){
         if (this.options.scrollTo === 'top' || likeReload){
             if (this.options.scrollSpeed == 1 || likeReload){
                 $('html, body').scrollTop(0);
             }else{
                 $('html, body').animate({scrollTop: 0}, this.options.scrollSpeed);
             }
         }else if(this.options.scrollTo !== false){
             if (this.options.scrollTo){
                 var offset = this.options.scrollTo.offset().top + this.options.scrollOffset;
             }else{
                 var offset = this.container.offset().top + this.options.scrollOffset;
             }
             if (this.options.scrollSpeed==1){
                 $('html, body').scrollTop(offset);
             }else{
                 $('html, body').animate({scrollTop: offset}, this.options.scrollSpeed);
             }             
         }         
     },
     _pageLoadCallback: function(data, likeReload){
         /*
          * This function is executed after page loading and update
          * metadata 
          */
         this.updateContent(data, likeReload);
         this.hideLoading(data, likeReload);
         this.scrollAfterUpdate(data, likeReload);

         data.total && this.totalValueNode.html(data.total);
         data.from && this.fromValueNode.html(data.from);
         data.to && this.toValueNode.html(data.to);
         data.pages && this.setPages(data.pages);
         
         if ( ! data.total){
             this.pageInfoNode.hide();
         }else{
             this.pageInfoNode.show();
         }
     },
     _checkNavigationLinks: function(){
         if (this.page == 1){
             this.prevLink.hide();
         }else{
             this.prevLink.show();
         };
         
         if ( ! this.pages || this.page == this.pages){
             this.nextLink.hide();
         }else{
             this.nextLink.show();
         };                 
     },
     showLoading: function(){
         this.pageInfoNode.hide();
         this.loadingIndicator.show();
         this.container.css('opacity', '0.4');
     },
     hideLoading: function(){
         this.loadingIndicator.hide();
         this.pageInfoNode.show();
         this.container.css('opacity', '');
     },             
     setPages: function(pages){
         /*
          * This is set from server after page loading.
          * So number of pages can change and we should check if current
          * page number is still valid. 
          * We may not reload data, because server will return last 
          * page if we send to large page number.
          */
         this.pages = pages;
         
         if (this.pages && this.page > this.pages){
             this.page = this.pages;
         };
         this._checkNavigationLinks();
     },
     refresh: function(likeReload){
         this.setPage(this.page, likeReload);
     },
     getAddressParams: function(){
        var parameters = {},
            parameterNames = $.address.parameterNames();
        for (var i = 0, l = parameterNames.length; i < l; i++) {
            parameters[parameterNames[i]] = $.address.parameter(parameterNames[i]);
        };
        return parameters;
     },
     setPage: function(page, likeReload){
         //this for changing page on document ready and with changing URL
         //so this looks like user reload page
         likeReload = likeReload || false;
         //check if page number is valid
         if (page <= 0){
             page = 1;
         };

         if (this.pages && page > this.pages){
             page = this.pages;
         }
         
         this.page = page;
         
         //hide/show navigation links
         this._checkNavigationLinks();
         
         //change URL
         if (page != 1 || $.address.parameter('page')){
             $.address.parameter('page', page);
         }
         
         //init timedout callback for page loading
         //this is for more quickly navigation, so we can quickly change 
         //few pages without waiting for loading
         if (this.timeoutId){
             clearTimeout(this.timeoutId);
             this.timeoutId = null;
         };
         var that = this;
         this.timeoutId = setTimeout(function(){
             that.showLoading();
             var cb = that._createDelegate(that._pageLoadCallback, [likeReload], that);
             that.onPageChange(that.page, cb, that.getAddressParams());
         }, 300);
     }
 });

})(jQuery);
