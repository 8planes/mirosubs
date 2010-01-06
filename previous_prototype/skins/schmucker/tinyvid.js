/* Styling originally from Hans Schmucker,
   http://www.tapper-ware.net/devel/js/JS.TinyVidPlayer/index.xhtml
 */

// Stop JSLint whinging about globals //
/*global document: true, window: true, ItextCollection: true, jQuery: true */

var das={
	hardScope:function(fn,sc){
		return function(){
			fn.apply(sc,arguments);
		};
	},
	EvtListener:function(el,type,call){
		this.add=das.hardScope(function(el){
			if(this.bound) {
			  this.remove();
			}
			this.data.el=el;
			el.addEventListener(this.data.type,this.data.call,false);
			this.bound=true;
		},this);
		this.remove=das.hardScope(function(){
			this.data.el.removeEventListener(this.data.type,this.data.call,false);
			this.bound=false;
		},this);
		
		this.data={el:el,type:type,call:call,bound:false};
		this.add(el);
	}
};


/*====== ThrobberHandle ======*/
var ThrobberHandle=function(element, interactiveReference,onInteract){
	this.setValue=das.hardScope(this.setValue,this);
	this.startInteract=das.hardScope(this.startInteract,this);
	this.doInteract=das.hardScope(this.doInteract,this);
	this.endInteract=das.hardScope(this.endInteract,this);
	this.interactive=!!interactiveReference;
	this.element=element;
	this.reference=interactiveReference;
	this.onInteract=onInteract;
	
	if(this.interactive) {
		this.mouseDownListener=new das.EvtListener(this.reference,"mousedown",this.startInteract);
	}
};

ThrobberHandle.prototype={
	blocked:false,
	onInteract:null,
	interactive:false,
	element:null,
	reference:null,
	value:0,
	setValue:function(val,overrideBlocked){
		if(this.blocked && !overrideBlocked) {
		  return;
		}
		this.value=val;
		this.element.style.left=(this.value*100)+"%";
	},
	mouseDownListener:null,
	mouseMoveListener:null,
	mouseUpListener:null,
	startInteract:function(evt){
		if(evt.button !== 0) {
		  return;
		}
		this.mouseMoveListener=new das.EvtListener(window,"mousemove",this.doInteract);
		this.mouseUpListener=new das.EvtListener(window,"mouseup",this.endInteract);
		this.doInteract(evt);
		this.blocked=true;
		evt.preventDefault();
	},
	doInteract:function(evt,end){
		var base=this.reference.getBoundingClientRect();
		var x=evt.pageX-base.left;
		var width=this.reference.offsetWidth;
		var p=x/width;
		if(p>1) {
			p=1;
		}
		if(p<0) {
			p=0;
		}
		this.setValue(p,true);
		this.onInteract(p,!!end);
	},
	endInteract:function(evt){
		if(evt.button !== 0) {
		  return;
		}
		this.mouseMoveListener.remove();
		this.mouseMoveListener=null;
		this.mouseUpListener.remove();
		this.mouseUpListener=null;
		
		this.doInteract(evt,true);
		this.blocked=false;
	}
};


/*====== ProgressHandle ======*/
var ProgressHandle=function(element, interactiveReference,onInteract){
	ThrobberHandle.call(this,element, interactiveReference,onInteract);
};
var ThrobberHandleInheritor=(function(){});
ThrobberHandleInheritor.prototype=ThrobberHandle.prototype;
ProgressHandle.prototype=new ThrobberHandleInheritor();

ProgressHandle.prototype.setValue=function(val,overrideBlocked){
	if(this.blocked && !overrideBlocked) {
		return;
	}
	this.value=val;
	this.element.style.width=(this.value*100)+"%";
};


/*====== LinkedResizer ======*/
var LinkedResizer=function(handle,target){
	this.startResize=das.hardScope(this.startResize,this);
	this.doResize=das.hardScope(this.doResize,this);
	this.endResize=das.hardScope(this.endResize,this);
	
	this.handle=handle;
	this.target=target;
	
	this.mouseDownListener=new das.EvtListener(this.handle,"mousedown",this.startResize);
};

LinkedResizer.prototype={
	handle:null,
	target:null,
	startX:0,startY:0,
	startWidth:0,startHeight:0,
	innerOffsetX:0,innerOffsetY:0,
	startResize:function(evt){
		if(evt.button !== 0) {
		  return;
		}
		this.mouseMoveListener=new das.EvtListener(window,"mousemove",this.doResize);
		this.mouseUpListener=new das.EvtListener(window,"mouseup",this.endResize);
		
		this.startX=evt.pageX;
		this.startY=evt.pageY;
		this.startWidth=this.target.offsetWidth;
		this.startHeight=this.target.offsetHeight;
		
		evt.preventDefault();
	},
	doResize:function(evt){
		var ox=evt.pageX-this.startX;
		var oy=evt.pageY-this.startY;

		var XdestX=this.startWidth+ox;
		var YdestX=this.startWidth+oy*(this.target.offsetWidth/this.target.offsetHeight);

		var destX=Math.max(XdestX,YdestX);
		
		if(destX<200) {
		  destX=200;
		}

		this.target.style.width=Math.floor(destX)+"px";
	},
	endResize:function(evt){
		if(evt.button !==0) {
		  return;
		}

		this.mouseMoveListener.remove();
		this.mouseMoveListener=null;
		this.mouseUpListener.remove();
		this.mouseUpListener=null;
		jQuery(".langMenu").css("height",jQuery(".v").css("height"));
	},
	mouseDownListener:null,
	mouseMoveListener:null,
	mouseUpListener:null
};


/*====== PlayerController ======*/
var PlayerController=function(el){
	this.play=das.hardScope(this.playpause,this);
//	this.stop=das.hardScope(this.stop,this);
	this.sound=das.hardScope(this.sound,this);
	this.itext=das.hardScope(this.itext,this);
	this.onProgress=das.hardScope(this.onProgress,this);
	this.onTimeChange=das.hardScope(this.onTimeChange,this);
	this.volumeChange=das.hardScope(this.volumeChange,this);
	this.seek=das.hardScope(this.seek,this);
	
	this.baseEl=el;
	this.video=this.baseEl.querySelector("video.v");
	this.volume=this.video.volume;
	this.soundImg = this.baseEl.querySelector("img.soundimg");
	
	this.playListener=new das.EvtListener(this.baseEl.querySelector("a.play"),"click",this.play);
	this.soundListener=new das.EvtListener(this.baseEl.querySelector("a.sound"),"click",this.sound);
	
	this.resizer=new LinkedResizer(this.baseEl.querySelector("div.size"),this.baseEl.querySelector("video.v"));
	
	this.progress=new ProgressHandle(this.baseEl.querySelector("div.seeker div.progress"));
	this.progressListener=new das.EvtListener(this.video,"progress",this.onProgress);
	
	this.position=new ThrobberHandle(this.baseEl.querySelector("div.seeker div.handle"),this.baseEl.querySelector("div.seeker div.limiter"),this.seek);
	this.positionListener=new das.EvtListener(this.video,"durationchanged",this.onTimeChange);
	this.timeListener=new das.EvtListener(this.video,"timeupdate",this.onTimeChange);
	this.timeMetaListener=new das.EvtListener(this.video,"loadedmetadata",this.onTimeChange);
	
	this.volumehandler=new ProgressHandle(this.baseEl.querySelector("div.volume div.progress"),this.baseEl.querySelector("div.volume div.fill"),this.volumeChange);
};

PlayerController.prototype={
	baseEl:null,
	video:null,
	playListener:null,
	stopListener:null,
	soundListener:null,
	visitext: false,
    soundImage:null,
	progressListener:null,
	positionListener:null,
	timeListener:null,
	timeMetaListener:null,
	volume:0,
	volumehandler:null,
	resizer:null,
	progress:null,
	position:null,
	play:function(){
		this.video.play();
	},
	playpause:function(){
		if (this.video.paused){
      this.video.play();
      this.baseEl.querySelector("a.play").setAttribute("paused", "false");
    } else {
      this.video.pause();
      this.baseEl.querySelector("a.play").setAttribute("paused", "true");
    }
	},
	stop:function(){
		this.video.pause();
	},
	sound:function(){
		this.video.muted=!this.video.muted;
		if (this.video.muted) {
			this.soundImg.src="skins/schmucker/images/soundoff.png";
		} else {
		    this.soundImg.src="skins/schmucker/images/sound.png";	
		}
	},
	volumeChange:function(p){
		this.volume=this.video.volume=p;
	},
	onProgress:function(evt){
		if(evt.lengthComputable && evt.total) {
		  this.progress.setValue(evt.loaded/evt.total);
		}
	},
	onTimeChange:function(evt){
		if(this.video.duration) {
		  this.position.setValue(this.video.currentTime/this.video.duration);
		} else {
		  this.position.setValue(0);
		}
	},
	seek:function(p,end){
		if(end) {
		  this.video.currentTime=this.video.duration*p;
		}
	}
};


/*====== main ======*/
var playerControllers=[];
window.addEventListener("load",function(){
	var playerElements=document.querySelectorAll("div.tinyVidPlayer");
	
	for(var i=0;i<playerElements.length;i++) {
		playerControllers.push(new PlayerController(playerElements[i]));
	}
},false);

