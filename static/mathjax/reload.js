String.prototype.replaceAll = function(search, replace){
  return this.split(search).join(replace);
}

django.jQuery( document ).ready(function() {
	if (document.getElementById('mathjaxquestion') != null )
	{
	cont = document.getElementById('mathjaxquestion').value;
	cont = cont.replaceAll("inf","infty");
	cont = cont.replace(/([\)\]\[]+)(n)([\(\[\]])/g,"$1nnn$3")
	cont = cont.replace(/([\)\]\[]+)(u)([\(\[\]])/g,"$1uuu$3")
	cont = cont.replaceAll(",",")(");

	fo = document.getElementsByClassName('field-inequalityquestion')[0];
	elem = document.createElement('p');
	elem.id = 'mathjaxquestionrepresentation';
	node = document.createTextNode("`" + cont + "`");
	elem.appendChild(node);
	fo.appendChild(elem);
	MathJax.Hub.Typeset('mathjaxquestionrepresentation');
	};

	if (document.getElementById('mathjaxanswer') != null )
	{
	cont = document.getElementById('mathjaxanswer').value;
	cont = cont.replaceAll("inf","infty");
	cont = cont.replace(/([\)\]\[]+)(n)([\(\[\]])/g,"$1nnn$3")
	cont = cont.replace(/([\)\]\[]+)(u)([\(\[\]])/g,"$1uuu$3")
	cont = cont.replaceAll(",",")(");

	fo = document.getElementsByClassName('field-inequalityanswer')[0];
	elem = document.createElement('p');
	elem.id = 'mathjaxanswerrepresentation';
	node = document.createTextNode("`" + cont + "`");
	elem.appendChild(node);
	fo.appendChild(elem);
	MathJax.Hub.Typeset('mathjaxanswerrepresentation');
	};
});

function updatemathjaxanswer() {
    cont = document.getElementById('mathjaxanswer').value;
	cont = cont.replaceAll("inf","infty");
	cont = cont.replace(/([\)\]\[]+)(n)([\(\[\]])/g,"$1nnn$3")
	cont = cont.replace(/([\)\]\[]+)(u)([\(\[\]])/g,"$1uuu$3")
	cont = cont.replaceAll(",",")(");

    document.getElementById('mathjaxanswerrepresentation').innerHTML = "`" + cont + "`";
    MathJax.Hub.Typeset('mathjaxanswerrepresentation');
    }

function updatemathjaxquestion() {
    cont = document.getElementById('mathjaxquestion').value;
	cont = cont.replaceAll("inf","infty");
	cont = cont.replace(/([\)\]\[]+)(n)([\(\[\]])/g,"$1nnn$3")
	cont = cont.replace(/([\)\]\[]+)(u)([\(\[\]])/g,"$1uuu$3")
	cont = cont.replaceAll(",",")(");

    document.getElementById('mathjaxquestionrepresentation').innerHTML = "`" + cont + "`";
    MathJax.Hub.Typeset('mathjaxquestionrepresentation');
    }
