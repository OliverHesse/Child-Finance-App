
modal_state = "closed"
selected = 0
const modal = document.getElementsByClassName("modal")[0]
const modalDate = document.getElementById("Date");
const modalChild = document.getElementById("Child");
const modalAmount = document.getElementById("Amount");

function MoreInfoPressed(btn){
  console.log(window.location.href);
  if(modal_state == "closed"){
    selected = parseInt(btn.parentElement.id,10);
    //populate data
    console.log(selected);
    console.log(data);
    modalDate.innerHTML = "Date: " + data[selected][2];
    modalChild.innerHTML = "Child: "+ data[selected][1];
    modalAmount.innerHTML = "Amount: £"+data[selected][3];
    modal_state = "open";
    modal.style.display = "flex";
  }
}
function CloseBtnPressed(btn){
  if(modal_state == "open"){
    modal_state = "closed";
    modal.style.display = "none";
  }
}

function post(path, params, method='post') {

  // The rest of this code assumes you are not using a library.
  // It can be made less verbose if you use one.
  const form = document.createElement('form');
  form.method = method;
  form.action = path;

  for (const key in params) {
    if (params.hasOwnProperty(key)) {
      const hiddenField = document.createElement('input');
      hiddenField.type = 'hidden';
      hiddenField.name = key;
      hiddenField.value = params[key];

      form.appendChild(hiddenField);
    }
  }

  document.body.appendChild(form);
  form.submit();
}
function AddChild(){
  redirect("/conceive_child")
}
function back(){
  redirect("/")
}
function redirect(dest){
  //gets me the base url
  //only needed whilst on replit
  url = window.location.href;
  curr_url = window.location.href.split("/");
  //+2 because of the removed //
  body_length = curr_url[0].length+curr_url[2].length+2;
  base = url.substring(0,body_length);


  window.location.replace(base+dest);
}
