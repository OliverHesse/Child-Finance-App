
const InfoModal = document.getElementById("more_info_modal");
const createRequestModal = document.getElementById("create_request_modal")
const requestHolder= document.getElementById("request_holder");
const transactionHolder = document.getElementById("transaction_holder")
const requestBtn = document.getElementById("request_tab")
const transactionBtn = document.getElementById("transaction_tab")
const ModalDate  = document.getElementById("Date");
const ModalParent  = document.getElementById("ModalParent");
const ModalChild  = document.getElementById("Mode_Child");
const ModalAccount = document.getElementById("Modal_Account");
const ModalAmount = document.getElementById("Amount");
const ModalType = document.getElementById("Type");
const ModalStatus = document.getElementById("Status");
const ModalNotes  = document.getElementById("notes_input_field");
const ModalBtnBox = document.getElementsByClassName("modal_btn_box")[0];
const request_title = document.getElementById("create_Title");
const id_btn = document.getElementsByClassName("request_modal_btn")[0];

var selected = -1;
var view_state = "requests";
var request_mode = "create";
function OpenRequestModal(btn){
  request_title.value="Create Request"
  id_btn.value = "Create Request"
  amount.value = ""
  notes.value = ""
  createRequestModal.style.display = "flex";
  request_mode = "create";
}

function openModal(btn){

  index = parseInt(btn.parentElement.id)
  console.log(parent);
  ModalParent.textContent ="Parent: "+ parent;
  ModalChild.textContent ="Child: "+children[actions[view_state][index][1]];
  ModalAccount.textContent ="Account:"+accounts[actions[view_state][index][2]];
  ModalAmount.textContent = "Amount: £"+actions[view_state][index][6];
  ModalDate.textContent = "Date: "+actions[view_state][index][5];
  ModalType.textContent = "Type: "+actions[view_state][index][3];
  ModalStatus.textContent = "Status: "+actions[view_state][index][4];
  ModalNotes.value = actions[view_state][index][7];
  if(actions[view_state][index][4] == "denied" ||actions[view_state][index][4] == "paid"||actions[view_state][index][4] == "insertion"){
    ModalBtnBox.style.display = "none";
  }else{
    ModalBtnBox.style.display = "block";
  }
  ModalBtnBox.id = index

  if(actions[view_state][index][4]=="pending" && actions[view_state][index][3] == "transaction"){
    showBtns();
  }else{
    hideBtns();
  }
  console.log("here lol")
  InfoModal.style.display = "flex";
    
}

function closeModal(btn){
    btn.parentElement.parentElement.parentElement.style.display = "none";
}

function back(){
  redirect("/")
}



function change_view(btn){
  
  if(btn.id == "request_tab"){
    view_state="requests"
    transactionBtn.classList.remove("selected")
    requestBtn.classList.add("selected");
    requestHolder.style.display = "flex";
    transactionHolder.style.display = "none";
  }else{
    view_state = "transactions"
    requestBtn.classList.remove("selected")
    transactionBtn.classList.add("selected");
    transactionHolder.style.display = "flex";
    requestHolder.style.display = "none";
  }
}
const amount = document.getElementById("amount")
const notes = document.getElementById("notes")
const children_select =  document.getElementById("children_select")
const account_select = document.getElementById("account_select")
function create_request(btn){
  let data = {account_id:account_select.value,amount:amount.value,notes:notes.value,type:btn.id}
  if(btn.id=="Parent"){
      data = Object.assign({child_id:children_select.value}, data)

  }
  //gets me the base url
  //only needed whilst on replit
  url = window.location.href;
  curr_url = window.location.href.split("/");
  //+2 because of the removed //
  body_length = curr_url[0].length+curr_url[2].length+2;
  base = url.substring(0,body_length);
  dest = "/append_transactions"
  
  if(request_mode == "edit"){
    dest = "/edit_request"
    id_holder = document.getElementsByClassName("index_holder")[0]
    id = actions["requests"][id_holder.id][0]
    data = Object.assign({request_id:id},data)
  }

  post(base+dest,data)
}

function get_id(index){
  
  return actions[view_state][index][0]
}

function accept_request(btn){

  post(stripped_href()+"/accept_request",{id:get_id(parseInt(btn.parentElement.id))})
}

function deny_request(btn){
   post(stripped_href()+"/deny_request",{id:get_id(parseInt(btn.parentElement.id))})
}

function pay_request(btn){

   post(stripped_href()+"/pay_pending",{id:get_id(parseInt(btn.parentElement.id))})
}

function edit_request(btn){
  closeModal(btn);
  //close_current_modal
  //open the request modal but edit it
  index = btn.parentElement.id 
  request_title.textContent = "Edit Request"
  id_btn.parentElement.id = index
  id_btn.innerHTML  = "Edit Request"
  amount.value = actions["requests"][index][6]
  notes.value = actions["requests"][index][7]
  account_select.value = actions["requests"][index][2]
  createRequestModal.style.display = "flex";
  request_mode = "edit"
  //post(stripped_href()+"/edit_request",{id:get_id(parseInt(btn.parentElement.id))})
}

function openChangeFilterModal(){
  console.log(document.getElementById("change_filter_modal"))
  document.getElementById("change_filter_modal").style.display = "flex";
}

function SetFilters(){
  filters = {
    "insertion":document.getElementById("insertionOption").checked,
    "paid":document.getElementById("paidOption").checked,
    "denied":document.getElementById("deniedOption").checked,
    "pending":document.getElementById("pendingOption").checked
  }
  //first loop through transactionHolder
  for (action of transactionHolder.children) {
    if (filters[actions["transactions"][action.id][4]] == false){
      action.style.display = "none"
    }else{
      action.style.display = "flex"
    }
  }
  //then requestHolder
  for (action of requestHolder.children) {
    if (filters[actions["requests"][action.id][4]] == false){
      action.style.display = "none"
    }else{
      action.style.display = "flex"
    }
  }
}
function redraw(){
  //template
  //<div id = "{{request_i}}" class = "action">
    //<div id = "action_total" class = "action_text"> {{actions["requests"][request_i][6]}}</div>
    //<div id = "action_status" class = "action_text"> {{actions["requests"][request_i][4]}}</div>
    //<button onclick="openModal(this)" id = "MoreInfoBtn" class = "action_btn">More Info</button>
  //</div>
  transactionHolder.innerHTML = ""
  for(let i = 0; i<actions["transactions"].length; i++){
    newAction = document.createElement("div");
    newAction.id = i;
    newAction.className = "action"
    
    total = document.createElement("div");
    total.id = "action_total"
    total.className = "action_text"
    total.innerHTML = actions["transactions"][i][6]
    new_status = document.createElement("div");
    new_status.id = "action_status"
    new_status.className = "action_text"
    new_status.innerHTML = actions["transactions"][i][4]
    
    
    MoreInfoBtn = document.createElement("button");
    MoreInfoBtn.id = "MoreInfoBtn"
    MoreInfoBtn.className = "action_btn"
    MoreInfoBtn.textContent = "More Info"
    MoreInfoBtn.addEventListener("click", function(btn) {
        return function() {
            // Call the function with the button as a parameter
            openModal(btn);
        };
    }(MoreInfoBtn));
    newAction.appendChild(total)
    newAction.appendChild(new_status)
    newAction.appendChild(MoreInfoBtn)
    transactionHolder.appendChild(newAction)
  }
  requestHolder.innerHTML = ""
  for(let i = 0; i<actions["requests"].length; i++){
    newAction = document.createElement("div");
    newAction.id = i;
    newAction.className = "action"
    total = document.createElement("div");
    total.id = "action_total"
    total.className = "action_text"
    total.innerHTML = actions["requests"][i][6]
    
    new_status = document.createElement("div");
    new_status.id = "action_status"
    new_status.className = "action_text"
    new_status.innerHTML = actions["requests"][i][4]
    
    MoreInfoBtn = document.createElement("button");
    MoreInfoBtn.id = "MoreInfoBtn"
    MoreInfoBtn.className ="action_btn"
    MoreInfoBtn.textContent = "More Info"
    MoreInfoBtn.addEventListener("click", function(btn) {
          return function() {
              // Call the function with the button as a parameter
              openModal(btn);
          };
      }(MoreInfoBtn));
    newAction.appendChild(total)
    newAction.appendChild(new_status)
    newAction.appendChild(MoreInfoBtn)
    requestHolder.appendChild(newAction)
  }
}
function updateOrder(OrderSelector){
  if(OrderSelector.value == "Total"){
    quicksort(actions["transactions"],0,actions["transactions"].length-1,6)
    quicksort(actions["requests"],0,actions["requests"].length-1,6)
    updateDirection("Keep")
    redraw()
  }else if (OrderSelector.value == "Date"){
    quicksort(actions["transactions"],0,actions["transactions"].length-1,5)
    quicksort(actions["requests"],0,actions["requests"].length-1,5)
    updateDirection("Keep")
    redraw()
  }
}
let direction = "Asc"

function updateDirection(Direction){
  //.reverse();
  console.log(Direction)
  if(Direction == "Keep"&& direction == "Desc"){
    actions["transactions"].reverse();
    actions["requests"].reverse();
  }
  if(direction != Direction && Direction !="Keep"){
    actions["transactions"].reverse();
    actions["requests"].reverse();
    direction = Direction
    redraw()
  }
}
