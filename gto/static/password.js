$(document).ready(function () {
   $("#password, #confirm_password").keyup(checkPasswordMatch);
});

function checkPasswordMatch() {
    var password = $("#password").val();
    var confirmPassword = $("#confirm_password").val();
    if (password.length < 6) {
        $("#val_message").html("Password should be at least 6 characters in length.");
        document.getElementById("submit_button").disabled = true;
    }
    else if (password != confirmPassword){
            $("#val_message").html("Passwords do not match!");
            document.getElementById("submit_button").disabled = true;
            
        }

    else{
            $("#val_message").html("");
            document.getElementById("submit_button").disabled = false;
        }
}