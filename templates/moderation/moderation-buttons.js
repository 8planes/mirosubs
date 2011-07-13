var APPROVE_MARKER = "moderation-set-button";
var LOADING_TEXT = "wait ...";
var batchURLS = [];




function updatePendingCount(num, absolute){
    var count = num;
    if (!absolute){
        count = parseInt($(".active .badgy ").text()) + count ;
    }
    $(".active .badgy ").text(count );
}

function hideRow(row){
    row.fadeOut(500, function(){
        var myTable = $(this).parents("table");
        
        $(this).remove();
        var numLangs = $("tr", myTable).length;
        // if it's the last one, we still heave the header
        if (numLangs == 1 ){
            // the header
            
            $(myTable).slideDown( 400, function(){
                $(this).parents(".video-container").remove();
            });
        }
    });    
}
function updateModPane(el, data){
    hideRow($(el).parents("tr"));
}

/**
 * Updates the ajax response on the video history panel. We need to change
 * the button (if we've just rejected a revision, we can now approve it) , 
 * and also the status icon under 'Most recent'
 */
function updateHistoryPanel(el, data){
    var newBT = $(data.new_button_html);
    $(el).before(newBT);
    $(el).remove();
    newBT.slideDown(200,function(){
        prepareApproveButton(0, this);
    });
    var statusHolder = $(newBT).parents("tr");
    $("div.moderation-status-icon", statusHolder).replaceWith(data.status_icon_html);
    

}
function showMessageFromResponse(response){
    var message = response.data.message || "An error ocurred, we're working on getting this fixes asap.";
    jQuery['jGrowl'](message, {'life': 10000});    
}
/*
 * Shows the message from response. If the element is passed.
 * we've succeeded, in which case we remove the row for this language, 
 * and if this was the last language for that video, we remove that also, 
 * and recrement the moderation pending notice.
 * 
 */
function onApproveDone(el, response){
    if (response.success){
        showMessageFromResponse(response)

    }
    if (el){
        var parentContainer = $(el).parents("tr.moderation-row");
        if (parentContainer.length && parentContainer.hasClass("moderation-panel-row")){
            updateModPane(el, response.data);
        }else if (parentContainer.hasClass("revision-history-row")){
            updateHistoryPanel(el, response.data);
        }
        updatePendingCount(response.data.pending_count, true);
    }
}

function prepareApproveButton(i, el){
    
    var url = $(el).attr('href');
    $(el).attr('#');
    $(el).click( function(e){
        e.preventDefault();
        if ($(this).hasClass("disabled")){
            return false;
        }
        var previousLabel = $(this).text();
        $(this).text(LOADING_TEXT);
        $(this).addClass("disabled");
        $(this).css("opacity", 0.5);
        var btn = $(this);
        $.ajax( {
            url: url,
            dataType: 'json',
            type: "POST",
            success: function(response){
                btn.text(previousLabel);
                btn.removeClass("disabled");
                onApproveDone(el, response);
            },
            error: function(response){
                onApproveDone(null, response);
            }
        });
    });

    
    
}

function ajaxifyApproveButtons(el){
    $("." + APPROVE_MARKER, el).each(prepareApproveButton);

}
ajaxifyApproveButtons();
window.ajaxifyApproveButtons = ajaxifyApproveButtons;
