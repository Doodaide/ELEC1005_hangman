
/* Submit letter */

$('#letter-form').submit(function(e) {
  var data = $("#letter-form").serialize();
  
  /* Empty input */
  $('#letter-form input').val('');
  
  $.ajax({
    type: "POST",
    url: '',
    data: data,
    success: function(data) {
      /* Refresh if finished */
      if (data.finished) {
        location.reload();
      }
      else {
        /* Update current */
        $('#current').text(data.current);
        
        /* Update errors */
        $('#errors').html(
          'Errors (' + data.errors.length + '/6): ' +
          '<span class="text-danger spaced">' + data.errors + '</span>');
          
        /* Update drawing */
        updateDrawing(data.errors);
      }
    }
  });
  e.preventDefault();
});

function updateDrawing(errors) {
  $('#hangman-drawing').children().slice(0,9).show();

  if (errors.length == 1) {
    $('#hangman-drawing').children().slice(9,13).show();

  } else if (errors.length == 6) {
    $('#hangman-drawing').children().slice(0, errors.length + 14).show();

  } else {
    $('#hangman-drawing').children().slice(12, errors.length + 12).show();
  }
}

