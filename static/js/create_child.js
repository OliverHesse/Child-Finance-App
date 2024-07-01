const usernameField = document.getElementById("username")
const passwordField = document.getElementById("password")


function SubmitData(){
  post(window.location.href,{username:usernameField.value,password:passwordField.value})
}
