$(document).ready(function () {
   $("#password").keyup(checkPasswordMatch);
});

function checkPasswordMatch() {
    var password = $("#password").val();
    if (!(password.match(/[a-z]/g) && password.match( 
                    /[A-Z]/g) && password.match( 
                    /[0-9]/g) && password.match( 
                    /[^a-zA-Z\d]/g) && password.length >= 8)) {
        $("#val_message").html("Passwords should contain 1 lowercase character, 1 uppercase character, 1 number and 1 special charcter. It should be at least 8 characters in length.");
        document.getElementById("submit_button").disabled = true;
    }
    else{
            $("#val_message").html("");
            document.getElementById("submit_button").disabled = false;
        }
}