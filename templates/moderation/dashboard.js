{% comment %} This has to be included in a onLoad handler ! {% endcomment %}
{% load i18n teams_tags paginator moderation utils_tags %}
goog.require("goog.structs.Set");
goog.require("mirosubs.SimpleWarning");
var ACTION_REJECTED = "rejected";
var ACTION_APPROVED = "approved";
var form = $('form.moderation-dashboard');
var batchApproveBt = $(".batch-approve-selected-button");
var batchRejectBt = $(".batch-reject-selected-button");
var q_input = form.find('input[name=q]');
var replaceSelector = ".moderation-list-container";
var loadingNode = $(replaceSelector).clone();

var sellectedIds = new goog.structs.Set();
var sellectedLangIds = new goog.structs.Set();
var sellectedEles = new goog.structs.Set();
var disabledClassName = "disabled";

function refreshBatchButtonState(){
    batchRejectBt.unbind("click");
    batchApproveBt.unbind("click");
    var enabled = sellectedIds.getCount() > 0;
    if (enabled){
        batchRejectBt.removeClass(disabledClassName);
        batchRejectBt.click(onBatchRejectRequested);
        batchApproveBt.removeClass(disabledClassName);
        batchApproveBt.click(onBatchApproveRequested);
    }else{
        batchRejectBt.addClass(disabledClassName);
        batchApproveBt.addClass(disabledClassName)
    }
}

function onBatchReturned(response, dialog){
    showMessageFromResonse(response)
    updatePendingCount(response.data.pending_count, true);
    dialog.setVisible(false);
    sellectedIds = new goog.structs.Set();
    sellectedLangIds = new goog.structs.Set();
    var els = sellectedEles.getValues();
    for (var i = 0 ; i < els.length; i ++){
        updateModPane($("td", els[i]).eq(0), {});
    }

    sellectedEles = new goog.structs.Set()
}

function onBatchConfirmed(action, dialog){
    console.log(sellectedEles.getValues());
    $.ajax({
        type: "POST",
        url: "{% url moderation:affect-selected team_id=team.pk %}",
        data: {
            ids: sellectedIds.getValues().join("-"), 
            lang_ids: sellectedLangIds.getValues().join("-"), 
            action: action
        },
        success: function(response){
            onBatchReturned(response, dialog);
        }
    });
    dialog.setVisible(false);
}

function onBatchApproveRequested(){
    console.log('ap')
    var d = new mirosubs.SimpleWarning(
        "Approve all", 
        "You should be super sure", 
        "Yeah, approve all", 
        function(){
            
            onBatchConfirmed(ACTION_APPROVED, d);
        },
        "No I changed my mind"
    );
    d.setVisible(true);
    return ;
    
}


function onBatchRejectRequested(){
    console.log(r);
    var d = new mirosubs.SimpleWarning(
        "Reject all", 
        "You should be super sure", 
        "Yeah, reject", 
        function(){
            alert("OK");
            onBatchConfirmed(ACTION_REJECTED, d);
        },
        "No don't"
    );
    d.setVisible(true);
    return ;
}

function initRow(i, rowEl){
    // if this is a table row, do nothing with it
    if ($("td", rowEl ).length == 0){
        return
    }
    var data = $(".approve-button-container", rowEl).attr("name").split(";");
    var id = data[0]
    var langId = data[1]
    
    $(".batch-apply", rowEl).change(function(e){
        if($(e.target).is(":checked")){
            sellectedIds.add(id);
            sellectedLangIds.add(langId);
            sellectedEles.add(rowEl);
        }else{
            sellectedIds.remove(id);
            sellectedLangIds.remove(langId);
            sellectedEles.remove(rowEl);
        }
        refreshBatchButtonState();
    });   
}

function showLoading(){
    $(replaceSelector).html(loadingNode.clone());
    $(replaceSelector).slideUp(300, function(){
    });
    
}


var onFormResults = function (res){
    var node = $(replaceSelector).html(res).hide().slideDown(300);
    $("tr", node).each(initRow);
    ajaxifyApproveButtons(node);
};

var handleForm = function(form){
    $.each(form.serializeArray(), function(i, item){
        $.address.parameter(item.name, item.value);
    });
    $.ajax({
        url: form.attr("action"),
        data: form.serializeArray(),
        success: onFormResults
    });
    $('.ajax-pagination').ajaxPaginator('setPage', 1);
};
function decorateItems(){
    form.submit(function(e){
        e.preventDefault();
        showLoading();
        handleForm($(this));
        return false;
    });
    
    //This is hack for FF. Don't know why but not "preventDefault",
    //not "return false" can't prevent submit on Enter press
    form.keypress(function(e){
        if (e.keyCode == 13){
            handleForm($(this));
            return false;
        }
    });
    handleForm(form);
    refreshBatchButtonState();
}

decorateItems();
