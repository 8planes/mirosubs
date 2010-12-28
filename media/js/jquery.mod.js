
// Modals - Navi 0.1
// Usage:
//    $.mod()
//    <a href="{fallback_url}" data-modal="{ID_of_modal}">Hey! Listen!</a>
jQuery.fn.mod = function(){
  var modal = $(this)

  // Create overlay mask
  var overlay = jQuery('<div>', {
    'class': 'overlay',
    'css': {
      'background-color': '#000',
      'opacity': 0.65,
      'position': 'fixed',
      'width': '100%',
      'height': '100%',
      'top': 0,
      'left': 0,
      'z-index': 1000
    }
  })

  // Close modal when overlay or close link is clicked    
  var close = function(){
    overlay.remove()
    modal.hide()
  }
  
  overlay.click(close)
  modal.find('[href="#close"]').click(function(e){
    e.preventDefault()
    close()
  })

  // Position modal
  modal.css({
    'position': 'fixed',
    'top': '50%',
    'left': '50%',
    'margin-left': -Math.floor(modal.width() / 2),
    'margin-top': -Math.floor(modal.height() / 2),
    'z-index': 1001
  })

  // Let there be light
  jQuery(document.body).append(overlay)
  try {
      if (!jQuery.contains(document.body, modal)) {
          jQuery(document.body).append(modal);
      }
  }catch(e){};

  modal.show();
}

jQuery.mod = function(){
  jQuery('[data-modal]').click(function(e){
    e.preventDefault()
    var modal = jQuery('#' + jQuery(this).attr('data-modal'))
    modal.mod()
  })
}