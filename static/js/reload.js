String.prototype.replaceAll = function(search, replace){
  return this.split(search).join(replace);
}

jQuery( document ).ready(function() {
	MathJax.Hub.Typeset('mathjaxquestion');
	updatemathjaxanswer();
});

function updatemathjaxanswer() {
	cont = document.getElementById('mathjaxanswer').value;
	cont = cont.replaceAll("inf","infty");
	cont = cont.replace(/([\)\]\[]+)(n)([\(\[\]])/g,"$1nnn$3")
	cont = cont.replace(/([\)\]\[]+)(u)([\(\[\]])/g,"$1uuu$3")
	cont = cont.replaceAll(",",")(");

    document.getElementById('mathjaxanswerrepresentation').innerHTML = "`" + cont + "`";
    MathJax.Hub.Typeset('mathjaxanswerrepresentation');
};

$(document).on('submit', '.inequality', function(){
$.ajax({ 
    type: $(this).attr('method'),
    url: this.action,
    data: $(this).serialize(),
    context: this,
    success: function(data, status) {
        if (data.isok == 'OK')
        { location.reload();  }
        else
        { $('.RET').html(data.isok); }
    }
    });
    return false;
});
