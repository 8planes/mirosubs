(function($){
 
    $.Rpc = $.inherit(jQuery.util.Observable, {
        exceptions: {
            TRANSPORT: 'xhr',
            PARSE: 'parse',
            LOGIN: 'login',
            SERVER: 'exception'
        },
      
        constructor: function(){
            this.addEvents(
                'event',
                'exception'
            );
            this.transactions = {};
            this.providers = {};        
        },
        
        addProvider : function(provider){
            var a = arguments;
            if(a.length > 1){
                for(var i = 0, len = a.length; i < len; i++){
                    this.addProvider(a[i]);
                }
                return;
            }          
              
            if(!provider.events){
                provider = new $.Rpc.RemotingProvider(provider);
            }
            provider.id = provider.id || $.guid++;
            this.providers[provider.id] = provider;
    
            provider.on('data', this.onProviderData, this);
            provider.on('exception', this.onProviderException, this);
    
            if(!provider.isConnected()){
                provider.connect();
            }
    
            return provider;
        },
    
        
        getProvider : function(id){
            return this.providers[id];
        },
    
        removeProvider : function(id){
            var provider = id.id ? id : this.providers[id];
            provider.un('data', this.onProviderData, this);
            provider.un('exception', this.onProviderException, this);
            delete this.providers[provider.id];
            return provider;
        },
    
        addTransaction: function(t){
            this.transactions[t.tid] = t;
            return t;
        },
    
        removeTransaction: function(t){
            delete this.transactions[t.tid || t];
            return t;
        },
    
        getTransaction: function(tid){
            return this.transactions[tid.tid || tid];
        },
    
        onProviderData : function(provider, e){
            if($.isArray(e)){
                for(var i = 0, len = e.length; i < len; i++){
                    this.onProviderData(provider, e[i]);
                }
                return;
            }
            if(e.name && e.name != 'event' && e.name != 'exception'){
                this.fireEvent(e.name, e);
            }else if(e.type == 'exception'){
                this.fireEvent('exception', e);
            }
            this.fireEvent('event', e, provider);
        },
    
        createEvent : function(response, extraProps){
            return new $.Rpc.eventTypes[response.type]($.extend(response, extraProps));
        }        
    });

    $.Rpc = new $.Rpc();

    $.Rpc.TID = 1;
    
    //Transaction
    $.Rpc.Transaction = function(config){
        $.extend(this, config);
        this.tid = ++$.Rpc.TID;
        this.retryCount = 0;
    };

    $.Rpc.Transaction.prototype = {
        send: function(){
            this.provider.queueTransaction(this);
        },
    
        retry: function(){
            this.retryCount++;
            this.send();
        },
    
        getProvider: function(){
            return this.provider;
        }
    };
    
    //Event
    $.Rpc.Event = function(config){
        $.extend(this, config);
    };

    $.Rpc.Event.prototype = {
        status: true,
        getData: function(){
            return this.data;
        }
    };
    
    $.Rpc.RemotingEvent = $.inherit($.Rpc.Event, {
        type: 'rpc',
        getTransaction: function(){
            return this.transaction || $.Rpc.getTransaction(this.tid);
        }
    });
    
    $.Rpc.ExceptionEvent = $.inherit($.Rpc.RemotingEvent, {
        status: false,
        type: 'exception'
    });

    $.Rpc.eventTypes = {
        'rpc':  $.Rpc.RemotingEvent,
        'event':  $.Rpc.Event,
        'exception':  $.Rpc.ExceptionEvent
    };
    
    //Provider
    $.Rpc.Provider = $.inherit($.util.Observable, {    
        
        priority: 1,
        
        constructor : function(config){
            $.extend(this, config);
            this.addEvents(
                'connect',
                'disconnect',
                'data',
                'exception'
            );
            $.Rpc.Provider.superclass.constructor.call(this, config);
        },
        
        isConnected: function(){
            return false;
        },
        
        connect: $.noop,
        
        disconnect: $.noop
    });
    
    $.Rpc.JsonProvider = $.inherit($.Rpc.Provider, {
        parseResponse: function(xhr){
            if(!$.isEmpty(xhr.responseText)){
                if(typeof xhr.responseText == 'object'){
                    return xhr.responseText;
                }
                return $.parseJSON(xhr.responseText);
            }
            return null;
        },
    
        getEvents: function(xhr){
            var data = null;
            try{
                data = this.parseResponse(xhr);
            }catch(e){
                var event = new $.Rpc.ExceptionEvent({
                    data: e,
                    xhr: xhr,
                    code: $.Rpc.exceptions.PARSE,
                    message: 'Error parsing json response: \n\n ' + data
                });
                return [event];
            }
            var events = [];
            if($.isArray(data)){
                for(var i = 0, len = data.length; i < len; i++){
                    events.push($.Rpc.createEvent(data[i]));
                }
            }else{
                events.push($.Rpc.createEvent(data));
            }
            return events;
        }
    }); 
    
    $.Rpc.RemotingProvider = $.inherit($.Rpc.JsonProvider, {       
        enableBuffer: 10,
        
        maxRetries: 1,
        
        timeout: undefined,
    
        constructor : function(config){
            $.Rpc.RemotingProvider.superclass.constructor.call(this, config);
            this.addEvents(
                'beforecall',            
                'call'
            );
            this.namespace = (typeof this.namespace == 'string') ? $.ns(this.namespace) : this.namespace || window;
            this.transactions = {};
            this.callBuffer = [];
        },
        
        initAPI : function(){
            var o = this.actions;
            for(var c in o){
                var cls = this.namespace[c] || (this.namespace[c] = {}),
                    ms = o[c];
                for(var i = 0, len = ms.length; i < len; i++){
                    var m = ms[i];
                    cls[m.name] = this.createMethod(c, m);
                }
            }
        },
        
        isConnected: function(){
            return !!this.connected;
        },
    
        connect: function(){
            if(this.url){
                this.initAPI();
                this.connected = true;
                this.fireEvent('connect', this);
            }else if(!this.url){
                throw 'Error initializing RemotingProvider, no url configured.';
            }
        },
    
        disconnect: function(){
            if(this.connected){
                this.connected = false;
                this.fireEvent('disconnect', this);
            }
        },
    
        onData: function(xhr, status, opt){
            if(status === 'success'){
                var events = this.getEvents(xhr);
                for(var i = 0, len = events.length; i < len; i++){
                    var e = events[i],
                        t = this.getTransaction(e);
                    this.fireEvent('data', this, e);
                    if(t){
                        this.doCallback(t, e, true);
                        $.Rpc.removeTransaction(t);
                    }
                }
            }else{
                var ts = [].concat(opt.ts);
                for(var i = 0, len = ts.length; i < len; i++){
                    var t = this.getTransaction(ts[i]);
                    if(t && t.retryCount < this.maxRetries){
                        t.retry();
                    }else{
                        var e = new $.Rpc.ExceptionEvent({
                            data: e,
                            transaction: t,
                            code: $.Rpc.exceptions.TRANSPORT,
                            message: 'Unable to connect to the server.',
                            xhr: xhr
                        });
                        this.fireEvent('data', this, e);
                        if(t){
                            this.doCallback(t, e, false);
                            $.Rpc.removeTransaction(t);
                        }
                    }
                }
            }
        },
    
        getCallData: function(t){
            return {
                action: t.action,
                method: t.method,
                data: t.data,
                tid: t.tid
            };
        },
    
        doSend : function(data){
            var o = {
                url: this.url,
                ts: data,
                type: 'POST',
                timeout: this.timeout,
                dataType: 'json'
            }, callData;
    
            if($.isArray(data)){
                callData = [];
                for(var i = 0, len = data.length; i < len; i++){
                    callData.push(this.getCallData(data[i]));
                }
            }else{
                callData = this.getCallData(data);
            }

            if(this.enableUrlEncode){
                var params = {};
                params[(typeof this.enableUrlEncode == 'string') ? this.enableUrlEncode : 'data'] = $.JSON.encode(callData);
                o.data = params;
            }else{
                o.data = $.JSON.encode(callData);
                o.processData = false;
            }
            o.complete = this.onData.createDelegate(this, o, true);
            $.ajax(o);
        },
    
        combineAndSend : function(){
            var len = this.callBuffer.length;
            if(len > 0){
                this.doSend(len == 1 ? this.callBuffer[0] : this.callBuffer);
                this.callBuffer = [];
            }
        },
    
        queueTransaction: function(t){
            if(t.form){
                this.processForm(t);
                return;
            }
            this.callBuffer.push(t);
            if(this.enableBuffer){
                if(!this.callTask){
                    this.callTask = new $.util.DelayedTask(this.combineAndSend, this);
                }
                this.callTask.delay($.isNumber(this.enableBuffer) ? this.enableBuffer : 10);
            }else{
                this.combineAndSend();
            }
        },
    
        doCall : function(c, m, args){
            var data = null, hs, scope, len = 0;
            $.each(args, function(i, val){
                if (! hs && $.isFunction(val)){
                    hs = val;
                    scope = args[i+1];
                    len = i;
                };
            });
    
            if(len !== 0){
                data = args.slice(0, len);
            }
            
            var t = new $.Rpc.Transaction({
                provider: this,
                args: args,
                action: c,
                method: m.name,
                data: data,
                cb: scope && $.isFunction(hs) ? hs.createDelegate(scope) : hs
            });
    
            if(this.fireEvent('beforecall', this, t) !== false){
                $.Rpc.addTransaction(t);
                this.queueTransaction(t);
                this.fireEvent('call', this, t);
            }
        },
        createMethod : function(c, m){
            var f = function(){
                this.doCall(c, m, Array.prototype.slice.call(arguments, 0));
            }.createDelegate(this);
            f.directCfg = {
                action: c,
                method: m
            };
            return f;
        },
    
        getTransaction: function(opt){
            return opt && opt.tid ? $.Rpc.getTransaction(opt.tid) : null;
        },
    
        doCallback: function(t, e){
            var fn = e.status ? 'success' : 'failure';
            if(t && t.cb){
                var hs = t.cb,
                    result = $.isDefined(e.result) ? e.result : e.data;
                if($.isFunction(hs)){
                    hs(result, e);
                } else{
                    hs[fn].apply(hs.scope, [result, e]); 
                    hs.callback.apply(hs.scope, [result, e]); 
                }
            }
        }
    });
     
})(jQuery);

