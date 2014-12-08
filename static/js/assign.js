django.jQuery( document ).ready(function() {
      if (window.location.pathname == '/wsgi/admin/inequality/testsassign/add/')
      {
      updatestudents()
      };
});

function updatestudents() {
	cval = django.jQuery("#id_studentgroup").val();
	if (cval != "")
		{
		django.jQuery("#id_studentsingroup option").remove()
		update_student_fields();
		}
		else
		{
		django.jQuery("#id_studentsingroup option").remove()
		};
};

function update_student_fields()
{
 cval = "value=" + django.jQuery("#id_studentgroup").val()
 django.jQuery.ajax({
    type: 'POST',
    url: "/wsgi/assign/",
    data: cval,
    success: function(data, status) {
        django.jQuery('#id_studentsingroup').html(data);
    }
    });
    return false;
};
