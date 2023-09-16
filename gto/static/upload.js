$(document).ready(function(){
  $('#file').change(function () {
  	for (var i = 0; i < this.files.length; i++) {
    $('#names').append(this.files[i].name + " \n");
  }
    
  });
});