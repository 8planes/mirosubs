{% comment %} should be shown inside a jQuery.load callback {%endcomment %}
    var warnShown = false;
    /*
      Make sure we always warn users befor un moderating a video.
      */
   function warnVideoUnmoderate(e){
       // show warning only once per video
       if (warnShown ){
           return;
       }
       var isSure = confirm("Are you sure? \n When this video is unmoderated: \n-All  versions awaiting moderation will be approved.\n-All rejected versions will be deleted- The current active version is the most recently approved one.");
       if (!isSure){
           e.preventDefault();
           return;
       }
       warnShown = true;
   }
        
    if ($("#id_is_moderated").is(":checked")){
        
        $("#id_is_moderated").click(warnVideoUnmoderate);
    }

