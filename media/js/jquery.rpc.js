jQuery.isObject = function(v){
    return !!v && Object.prototype.toString.call(v) === '[object Object]';
};

jQuery.isNumber = function(v){
    return typeof v === 'number' && isFinite(v);
};


jQuery.isEmpty = function(v, allowBlank){
    return v === null || v === undefined || ((jQuery.isArray(v) && !v.length)) || (!allowBlank ? v === '' : false);
};

jQuery.isDefined = function(v){
    return typeof v !== 'undefined';
};

jQuery.namespace = function(){
    var o, d;
    jQuery.each(arguments, function(i, v){
        d = v.split(".");
        o = window[d[0]] = window[d[0]] || {};
        jQuery.each(d.slice(1), function(i, v2){
            o = o[v2] = o[v2] || {};
        });
    });
    return o;
};

jQuery.ns = jQuery.namespace;

jQuery.JSON = {
    useHasOwn: ({}.hasOwnProperty ? true : false),
    pad: function(n){
        return n < 10 ? "0" + n : n;
    },
    m: {
        "\b": '\\b',
        "\t": '\\t',
        "\n": '\\n',
        "\f": '\\f',
        "\r": '\\r',
        '"': '\\"',
        "\\": '\\\\'
    },
    encodeString: function(s){
        if (/["\\\x00-\x1f]/.test(s)) {
            return '"' +
            s.replace(/([\x00-\x1f\\"])/g, function(a, b){
                var c = jQuery.JSON.m[b];
                if (c) {
                    return c;
                }
                c = b.charCodeAt();
                return "\\u00" +
                Math.floor(c / 16).toString(16) +
                (c % 16).toString(16);
            }) +
            '"';
        }
        return '"' + s + '"';
    },
    encodeArray: function(o){
        var a = ["["], b, i, l = o.length, v;
        for (i = 0; i < l; i += 1) {
            v = o[i];
            switch (typeof v) {
                case "undefined":
                case "function":
                case "unknown":
                    break;
                default:
                    if (b) {
                        a.push(',');
                    }
                    a.push(v === null ? "null" : this.encode(v));
                    b = true;
            }
        }
        a.push("]");
        return a.join("");
    },
    encodeDate: function(o){
        return '"' + o.getFullYear() + "-" +
        pad(o.getMonth() + 1) +
        "-" +
        pad(o.getDate()) +
        "T" +
        pad(o.getHours()) +
        ":" +
        pad(o.getMinutes()) +
        ":" +
        pad(o.getSeconds()) +
        '"';
    },
    encode: function(o){
        if (typeof o == "undefined" || o === null) {
            return "null";
        }
        else 
            if (o instanceof Array) {
                return this.encodeArray(o);
            }
            else 
                if (o instanceof Date) {
                    return this.encodeDate(o);
                }
                else 
                    if (typeof o == "string") {
                        return this.encodeString(o);
                    }
                    else 
                        if (typeof o == "number") {
                            return isFinite(o) ? String(o) : "null";
                        }
                        else 
                            if (typeof o == "boolean") {
                                return String(o);
                            }
                            else {
                                var self = this;
                                var a = ["{"], b, i, v;
                                for (i in o) {
                                    if (!this.useHasOwn || o.hasOwnProperty(i)) {
                                        v = o[i];
                                        switch (typeof v) {
                                            case "undefined":
                                            case "function":
                                            case "unknown":
                                                break;
                                            default:
                                                if (b) {
                                                    a.push(',');
                                                }
                                                a.push(self.encode(i), ":", v === null ? "null" : self.encode(v));
                                                b = true;
                                        }
                                    }
                                }
                                a.push("}");
                                return a.join("");
                            }
    },
    decode: function(json){
        return eval("(" + json + ')');
    }
};

jQuery.override = function(origclass, overrides){
    if(overrides){
        var p = origclass.prototype;
        jQuery.extend(p, overrides);
        if(jQuery.browser.msie && overrides.hasOwnProperty('toString')){
            p.toString = overrides.toString;
        }
    }
};

Function.prototype.createDelegate = function(obj, args, appendArgs){
    var method = this;
    return function() {
        var callArgs = args || arguments;
        if (appendArgs === true){
            callArgs = Array.prototype.slice.call(arguments, 0);
            callArgs = callArgs.concat(args);
        }else if ($.isNumber(appendArgs)){
            callArgs = Array.prototype.slice.call(arguments, 0); // copy arguments first
            var applyArgs = [appendArgs, 0].concat(args); // create method call params
            Array.prototype.splice.apply(callArgs, applyArgs); // splice them in
        }
        return method.apply(obj || window, callArgs);
    };
};

jQuery.inherit = function(){
    // Copy of Ext.extend from Ext-Core
    var io = function(o){
        for (var m in o) {
            this[m] = o[m];
        }
    };
    var oc = Object.prototype.constructor;
    
    return function(sb, sp, overrides){
        if (jQuery.isObject(sp)) {
            overrides = sp;
            sp = sb;
            sb = overrides.constructor != oc ? overrides.constructor : function(){
                sp.apply(this, arguments);
            };
        }
        var F = function(){
        }, sbp, spp = sp.prototype;
        
        F.prototype = spp;
        sbp = sb.prototype = new F();
        sbp.constructor = sb;
        sb.superclass = spp;
        if (spp.constructor == oc) {
            spp.constructor = sp;
        }
        sb.override = function(o){
            jQuery.override(sb, o);
        };
        sbp.superclass = sbp.supr = (function(){
            return spp;
        });
        sbp.override = io;
        jQuery.override(sb, overrides);

        sb.inherit = function(o){
            return jQuery.inherit(sb, o);
        };
        return sb;
    };
}();

jQuery.util = jQuery.util || {};

jQuery.util.Event = function(obj, name){
    this.name = name;
    this.obj = obj;
    this.listeners = [];
};

jQuery.util.Event.prototype = {
    addListener: function(fn, scope, options){
        var me = this, l;
        scope = scope || me.obj;
        if (!me.isListening(fn, scope)) {
            l = me.createListener(fn, scope, options);
            if (me.firing) { // if we are currently firing this event, don't disturb the listener loop
                me.listeners = me.listeners.slice(0);
            }
            me.listeners.push(l);
        }
    },
    
    createListener: function(fn, scope, o){
        o = o || {}, scope = scope || this.obj;
        var l = {
            fn: fn,
            scope: scope,
            options: o
        }, h = fn;
        l.fireFn = h;
        return l;
    },
    
    isListening: function(fn, scope){
        return this.findListener(fn, scope) != -1;
    },
    
    findListener: function(fn, scope){
        var list = this.listeners, i = list.length, l;
        
        scope = scope || this.obj;
        while (i--) {
            l = list[i];
            if (l) {
                if (l.fn == fn && l.scope == scope) {
                    return i;
                }
            }
        }
        return -1;
    },
    
    removeListener: function(fn, scope){
        var index, l, k, me = this, ret = false;
        if ((index = me.findListener(fn, scope)) != -1) {
            if (me.firing) {
                me.listeners = me.listeners.slice(0);
            }
            l = me.listeners[index];
            if (l.task) {
                l.task.cancel();
                delete l.task;
            }
            k = l.tasks && l.tasks.length;
            if (k) {
                while (k--) {
                    l.tasks[k].cancel();
                }
                delete l.tasks;
            }
            me.listeners.splice(index, 1);
            ret = true;
        }
        return ret;
    },
    
    // Iterate to stop any buffered/delayed events
    clearListeners: function(){
        var me = this, l = me.listeners, i = l.length;
        while (i--) {
            me.removeListener(l[i].fn, l[i].scope);
        }
    },
    
    fire: function(){
        var me = this, args = jQuery.makeArray(arguments), listeners = me.listeners, len = listeners.length, i = 0, l;
        
        if (len > 0) {
            me.firing = true;
            for (; i < len; i++) {
                l = listeners[i];
                if (l && l.fireFn.apply(l.scope || me.obj || window, args) === false) {
                    return (me.firing = false);
                }
            }
        }
        me.firing = false;
        return true;
    }
};

jQuery.util.Observable = function(){

    var me = this, e = me.events;
    if (me.listeners) {
        me.on(me.listeners);
        delete me.listeners;
    }
    me.events = e || {};
};

jQuery.util.Observable.prototype = {
    // private
    filterOptRe: /^(?:scope|delay|buffer|single)$/,
    
    fireEvent: function(){
        var a = jQuery.makeArray(arguments), ename = a[0].toLowerCase(), me = this, ret = true, ce = me.events[ename], q, c;
        if (me.eventsSuspended === true) {
            if (q = me.eventQueue) {
                q.push(a);
            }
        }
        else 
            if (jQuery.isObject(ce) && ce.bubble) {
                if (ce.fire.apply(ce, a.slice(1)) === false) {
                    return false;
                }
                c = me.getBubbleTarget && me.getBubbleTarget();
                if (c && c.enableBubble) {
                    if (!c.events[ename] || !jQuery.isObject(c.events[ename]) || !c.events[ename].bubble) {
                        c.enableBubble(ename);
                    }
                    return c.fireEvent.apply(c, a);
                }
            }
            else {
                if (jQuery.isObject(ce)) {
                    a.shift();
                    ret = ce.fire.apply(ce, a);
                }
            }
        return ret;
    },
    
    addListener: function(eventName, fn, scope, o){
        var me = this, e, oe, isF, ce;
        if (jQuery.isObject(eventName)) {
            o = eventName;
            for (e in o) {
                oe = o[e];
                if (!me.filterOptRe.test(e)) {
                    me.addListener(e, oe.fn || oe, oe.scope || o.scope, oe.fn ? oe : o);
                }
            }
        }
        else {
            eventName = eventName.toLowerCase();
            ce = me.events[eventName] || true;
            if (typeof ce === 'boolean') {
                me.events[eventName] = ce = new jQuery.util.Event(me, eventName);
            }
            ce.addListener(fn, scope, jQuery.isObject(o) ? o : {});
        }
    },
    
    removeListener: function(eventName, fn, scope){
        var ce = this.events[eventName.toLowerCase()];
        if (jQuery.isObject(ce)) {
            ce.removeListener(fn, scope);
        }
    },
    
    purgeListeners: function(){
        var events = this.events, evt, key;
        for (key in events) {
            evt = events[key];
            if (jQuery.isObject(evt)) {
                evt.clearListeners();
            }
        }
    },
    
    addEvents: function(o){
        var me = this;
        me.events = me.events || {};
        if (typeof o === 'string') {
            var a = arguments, i = a.length;
            while (i--) {
                me.events[a[i]] = me.events[a[i]] || true;
            }
        }
        else {
            Ext.applyIf(me.events, o);
        }
    },
    
    hasListener: function(eventName){
        var e = this.events[eventName.toLowerCase()];
        return jQuery.isObject(e) && e.listeners.length > 0;
    }
};

jQuery.util.Observable.prototype.on = jQuery.util.Observable.prototype.addListener;
jQuery.util.Observable.prototype.un = jQuery.util.Observable.prototype.removeListener;

//jQuery.util.DelayedTask
jQuery.util.DelayedTask = function(fn, scope, args){
    var me = this,
        id,     
        call = function(){
            clearInterval(id);
            id = null;
            fn.apply(scope, args || []);
        };
        
    me.delay = function(delay, newFn, newScope, newArgs){
        me.cancel();
        fn = newFn || fn;
        scope = newScope || scope;
        args = newArgs || args;
        id = setInterval(call, delay);
    };

    me.cancel = function(){
        if(id){
            clearInterval(id);
            id = null;
        }
    };
};

/* jQuery.Rpc */
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
                            data: ts[i].data,
                            transaction: t,
                            code: $.Rpc.exceptions.TRANSPORT,
                            message: 'Cannot connect to server. Please check your web connection.',
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
                o.data = $.param(params);
            }else{
                o.data = encodeURIComponent($.JSON.encode(callData));
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
            var data = null, cb, scope, len = 0;

            $.each(args, function(i, val){
                if ($.isFunction(val)){
                    return false;
                }
                len = i+1;
            });

            if(len !== 0){
                data = args.slice(0, len);
            }

            if (args[len+1] && $.isFunction(args[len+1])){
                //we have failure callback after success
                scope = args[len+2];
                cb = {
                    success: scope && $.isFunction(args[len]) ? args[len].createDelegate(scope) : args[len],
                    failure: scope ? args[len+1].createDelegate(scope) : args[len+1]
                }
                scope = args[len+2];
            }else{
                scope = args[len+1];
                cb = args[len] || $.noop;
                cb = scope && $.isFunction(cb) ? cb.createDelegate(scope) : cb;               
            }

            var t = new $.Rpc.Transaction({
                provider: this,
                args: args,
                action: c,
                method: m.name,
                data: data,
                cb: cb
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

