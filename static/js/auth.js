
active_tab = "login" //can only be login or sign
const username = document.getElementById("username")
const password = document.getElementById("password")
const sign = document.getElementById("sign")
const login = document.getElementById("login")
function change_tab(e){
  //for debuging
  if(sign.value.trim() != "" || login.value.trim() != ""){
    console.log("error: cant have blank fields")
    return
  }
  //swap the active tab
  if(active_tab == "login"){
    active_tab = "sign"
    //swap to sign
    sign.classList.add("selected")
    sign.classList.add("selected-right")
    login.classList.remove("selected")
    login.classList.remove("selected-left")
  }else{
    active_tab = "login"
    //swap to sign
    login.classList.add("selected")
    login.classList.add("selected-left")
    sign.classList.remove("selected")
    sign.classList.remove("selected-right")
  }
}
//send data to the server to be proccesed
function submit(e){
  console.log("something submited")
  post("/authenticate_user",{username:username.value,password:password.value,type:active_tab})
}
