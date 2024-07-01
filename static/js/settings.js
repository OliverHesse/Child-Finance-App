
const change_password_modal = document.getElementById("changePasswordModal")
const passwordField1 = document.getElementById("passwordField1")
const passwordField2= document.getElementById("passwordField2")
function open_change_password_modal(){
  console.log(change_password_modal)
  console.log("clicekd")
  change_password_modal.parentElement.style.display="flex"
  passwordField1.value = ""
  passwordField2.value = ""
}
function close_change_password_modal(){
  change_password_modal.parentElement.style.display="none"
}
function change_passwor(){
  post(stripped_href() + "/change_password",{p1:passwordField1.value,p2:passwordField2.value})
}

function restore_default(){
  usernameField.value = default_data[0]
}

function save_changes(){
  post(stripped_href() + "/change_details",{username:usernameField.value})
}

function back(){
  redirect("/")
}
