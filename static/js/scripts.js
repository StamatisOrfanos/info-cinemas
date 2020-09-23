// $("form[name=signUp_form").submit(function(e) {

//   var $form = $(this);
//   var $error = $form.find(".error");
//   var data = $form.serialize();

//   $.ajax({
//     url: "/app/signUp",
//     type: "POST",
//     data: data,
//     dataType: "json",
//     success: function(resp) {
//       window.location.href = "//";
//     },
//     error: function(resp) {
//       $error.text(resp.responseJSON.error).removeClass("error--hidden");
//     }
//   });

//   e.preventDefault();
// });

// $("form[name=signIn_form").submit(function(e) {

//   var $form = $(this);
//   var $error = $form.find(".error");
//   var data = $form.serialize();

//   $.ajax({
//     url: "/authentication/signIn",
//     type: "POST",
//     data: data,
//     dataType: "json",
//     success: function(resp) {
//       window.location.href = "/au/signIn/";
//     },
//     error: function(resp) {
//       $error.text(resp.responseJSON.error).removeClass("error--hidden");
//     }
//   });

//   e.preventDefault();
// });