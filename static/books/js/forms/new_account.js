function checkPasswords(){
	var pass = $('#id_password').val();
	var pass2 = $('#id_confirm_password').val();
	console.log('Passes: ' + pass +'  -  '+ pass2);
	if(pass != pass2){

	    $('#id_password').addClass('bad-password-input');
		$('#id_confirm_password').addClass('bad-password-input');

		$('#id_password').removeClass('good-password-input');
		$('#id_confirm_password').removeClass('good-password-input');
	} else {
		$('#id_password').addClass('good-password-input');
		$('#id_confirm_password').addClass('good-password-input');
	}
}

$(document).ready(function(){
    $('#id_confirm_password').on('input', function(){
        checkPasswords();
    });

    $('#id_password').on('input', function(){
        checkPasswords();
    });
});