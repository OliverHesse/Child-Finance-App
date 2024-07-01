
modal_state = "closed"
active_modal = "accounts"
selected = 0
const modal = document.getElementsByClassName("modal")[0]
const modalDate = document.getElementById("Date");
const modalChild = document.getElementById("Child");
const modalAmount = document.getElementById("Amount");
const child_accounts = document.getElementById("child_accounts");

function AddChild(){
  redirect("/conceive_child")
}
function AddAccount(){
  redirect("/create_account")
}
function AddPayment(){
  redirect("/create_payment")
}
function back(){
  redirect("/")
}


function manage_account_pressed(btn){
  id = data["accounts"][btn.parentElement.id][0]
  redirect("/manage_account?id="+id)
}

const setModals = {
  "accounts":openAccounts,
  "children":openChildren,
  "payment":openPayment
}
const closeModals = {
  "accounts":closeAccounts,
  "children":closeChildren,
  "payment":closePayment
}
function closeAccounts(){
  modal_window = document.getElementById("account_more_info_modal");
  modal_window.style.display = "none";
  modal.style.display = "none";
}
function openAccounts(){
  console.log("here2");
  modal_window = document.getElementById("account_more_info_modal");
  //set the value of all the data fields
  document.getElementById("accountDate").innerHTML = "Date: "+ data["accounts"][selected][3]
  document.getElementById("accountParent").innerHTML = "Parent: "+data["accounts"][selected][1]
  document.getElementById("accountTotal").innerHTML = "Total: £"+data["accounts"][selected][6]
  document.getElementById("account_notes").value = data["accounts"][selected][4]
  //construct a multiline string of children
  output_string = ""
  console.log(data["accounts"][selected][7])
  for(child in data["accounts"][selected][7]){
    
    output_string += data["accounts"][selected][7][child]+"\n"
  }
  document.getElementById("account_children").value = output_string;
  
  modal_window.style.display = "flex";
  modal.style.display = "flex";
}
function closeChildren(){
  modal_window = document.getElementById("child_more_info_modal");
  modal_window.style.display = "none";
  modal.style.display = "none";
}
function openChildren(){
  console.log("here2");
  //populate modal
  //data["children"][index]
  //data["children"][index]["Accounts"]

  document.getElementById("Date").innerHTML= "Date: "+data["children"][selected]["Date"];
  
  document.getElementById("Child").innerHTML= "Child: "+data["children"][selected]["Username"];
  
  document.getElementById("Amount").innerHTML="Total: £"+data["children"][selected]["Total"];
  output_string = ""
  for(account in data["children"][selected]["Accounts"]){
    output_string+=data["children"][selected]["Accounts"][account]+"\n"
  }
  child_accounts.value = output_string
  modal_window = document.getElementById("child_more_info_modal");
  modal_window.style.display = "flex";
  modal.style.display = "flex";
}
function closePayment(){
  modal_window = document.getElementById("payment_more_info_modal");
  modal_window.style.display = "none";
  modal.style.display = "none";
}
function openPayment(){
  document.getElementById("paymentNameField").innerHTML = "Name: "+data["payment"][selected][1]
  document.getElementById("paymentChild").innerHTML = "Child: "+data["payment"][selected][2]
  document.getElementById("paymentAccount").innerHTML = "Account: "+data["payment"][selected][3]
  document.getElementById("paymentTotal").innerHTML = "Total: £"+data["payment"][selected][4]
  document.getElementById("paymentFrequency").innerHTML = "Frequency: "+data["payment"][selected][5]+" Days"
  document.getElementById("paymentNotes").value = data["payment"][selected][6]
  modal_window = document.getElementById("payment_more_info_modal");
  modal_window.style.display = "flex";
  modal.style.display = "flex";
}
function openModal(btn){
  console.log("here")
  selected = parseInt(btn.parentElement.id)
  setModals[active_modal]()
}
function closeModal(btn){
  closeModals[active_modal]()
}
const holders = {
  "accounts":document.getElementById("account_holder"),
  "children":document.getElementById("child_holder"),
  "payment":document.getElementById("payment_holder")
}
const tab_btn={
  "accounts":document.getElementById("account_tab"),
  "children":document.getElementById("child_tab"),
  "payment":document.getElementById("payment_tab")
}
const swap={
  "accounts":"add_account_btn",
  "children":"add_child_btn",
  "payment":"add_payment_btn"
}
const swap2={
  "account_tab":"add_account_btn",
  "child_tab":"add_child_btn",
  "payment_tab":"add_payment_btn"
}
function change_tab(btn){
  holders[active_modal].style.display = "none";
  tab_btn[active_modal].classList.remove("selected");

  if(btn.id == "account_tab"){
    //open account_tab
    change_btn(swap[active_modal],swap2[btn.id])
    active_modal = "accounts"
    holders["accounts"].style.display = "flex";
    tab_btn["accounts"].classList.add("selected");
    
  }else if(btn.id == "child_tab"){
    //open child_tab
    change_btn(swap[active_modal],swap2[btn.id])
    active_modal = "children"
    holders["children"].style.display = "flex";
    tab_btn["children"].classList.add("selected")
   
  }else if(btn.id == "payment_tab"){
    //open payment_tab
    change_btn(swap[active_modal],swap2[btn.id])
    active_modal = "payment"
    holders["payment"].style.display = "flex";
    tab_btn["payment"].classList.add("selected")
    
  }
}

function changeFilters(filterColumn){
  //reorder all of payments children and accounts
  account_index = -1
  payment_index = -1
  child_index = -1
  //set the correct "pivot" column
  if(filterColumn =="Date"){
    account_index = 3
    payment_index = 8
    child_index = "Date"
  }else if (filterColumn == "Total"){
    account_index = 6
    payment_index = 4
    child_index = "Total"
  }else{
    //quick escape because it was either none or had a manual value inputed
    return 
  }
  quicksort(data["accounts"],0,data["accounts"]-1,account_index)
  quicksort(data["payment"],0,data["payments"]-1,payment_index)
  quicksort(data["children"],0,data["children"]-1,child_index)
  fixDirection("keep")
  redraw()
}
Direction = "Asc"
function fixDirection(newDirection){
  console.log(Direction)
  if(newDirection == "keep"&& Direction == "Desc"){
    data["children"].reverse();
    data["payment"].reverse()
    data["accounts"].reverse()

  }
  if(newDirection != Direction && newDirection !="keep"){
    data["children"].reverse();
    data["payment"].reverse()
    data["accounts"].reverse()

    Direction =newDirection
    redraw()
  }
}
let key_to_id = {
  "accounts":{
    "name":"account_name",
    "total":"account_total"
  },
  "children":{
      "name":"child_name",
      "total":"child_account"
    },
  "payment":{
      "name":"paymentName",
      "total":"paymentTotal"
    },
}
let tab_to_column_i = {
  "accounts":{"Username":2,"Total":6},
  "children":{"Username":"Username","Total":"Total"},
  "payment":{"Username":1,"Total":4},
}
function redraw(){
  //templating
  //<div id = "{{child_i}}" class = "child">
  //  <div id = "child_name" class = "child_text manage_name_field"> {{data["children"][child_i]["Username"]}}</div>
  //  <div id = "child_amount" class = "child_text manage_total_field">£{{data["children"][child_i]["Total"]}}</div>
  //  <button id = "MoreInfoBtn" class = "child_btn" onclick="openModal(this)">More Info</button>
  //</div>
  for(key in holders){
    holders[key].innerHTML = ""
    for(record_i in data[key]){
      info_holder = document.createElement("div")
      info_holder.id = record_i
      info_holder.className = "child"

      name_holder = document.createElement("div")
      name_holder.id = key_to_id[key]["name"]
      name_holder.className = "child_text manage_name_field"
      name_holder.innerHTML = data[key][record_i][tab_to_column_i[key]["Username"]]

      amount_holder = document.createElement("div")
      amount_holder.id = key_to_id[key]["total"]
      amount_holder.className = "child_text manage_total_field"
      amount_holder.innerHTML = "£"+data[key][record_i][tab_to_column_i[key]["Total"]]

      MoreInfoBtn = document.createElement("button");
      MoreInfoBtn.id = "MoreInfoBtn"
      MoreInfoBtn.className ="child_btn"
      MoreInfoBtn.textContent = "More Info"
      MoreInfoBtn.addEventListener("click", function(btn) {
        return function() {
            // Call the function with the button as a parameter
            openModal(btn);
        };
      }(MoreInfoBtn));
      info_holder.appendChild(name_holder)
      info_holder.appendChild(amount_holder)
      info_holder.appendChild(MoreInfoBtn)
      holders[key].appendChild(info_holder)

    }
  }
}