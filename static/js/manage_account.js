
const detailsTab = document.getElementById("detailsTab");
const childrenTab = document.getElementById("childrenTab");
const addFundsModal = document.getElementById("addFundsModal");
const moreInfoModal = document.getElementById("moreInfoModal");
const modal = document.getElementById("modal");
current_tab = "detailsTab"

function change_tab(btn){
  if(btn.id == "childrenBtn"){
    btn.classList.add("selected")
    document.getElementById("detailsBtn").classList.remove("selected")

    detailsTab.style.display = "none";
    childrenTab.style.display = "block";
  }else if(btn.id == "detailsBtn"){
    btn.classList.add("selected")
    document.getElementById("childrenBtn").classList.remove("selected")


    detailsTab.style.display = "block";
    childrenTab.style.display = "none";
  }
}
function closeModal(btn){
  modal.style.display = "none";
}
function openFundsModal(){
  modal.style.display="flex";
  addFundsModal.style.display = "flex";
  moreInfoModal.style.display = "none";
}
function openInfoModal(btn){
  index = btn.parentElement.id
  //populate modal with child data
  //first get refrences to the components i need
  date = document.getElementById("Date")
  child_name = document.getElementById("Child")
  amount = document.getElementById("Amount")
  date.innerHTML = "Date:" + account_details["children"][index][3]
  child_name.innerHTML = "Child:" + account_details["children"][index][2]
  amount.innerHTML = "Amount: £" + account_details["children"][index][1]
  
  modal.style.display="flex";
  addFundsModal.style.display = "none";
  moreInfoModal.style.display = "flex";
}
const childSelector = document.getElementById("children_select")
const Amount = document.getElementById("add_funds_amount")
const Notes = document.getElementById("add_funds_notes")
function addFunds(){
  let data = {amount:Amount.value,notes:Notes.value,type:"insertion",child_id:childSelector.value,account_id:account_details["data"][0]}
  post(stripped_href()+"/append_transactions",data)
}


function SaveChanges(){
  name_field = document.getElementById("name_field")
  descr_field = document.getElementById("descr_field")

  post(window.location.href,{id:account_details["data"][0],name:name_field.value,notes:descr_field.value})
}
function RestoreDefault(){
  //reset values back to origional
  document.getElementById("name_field").value=account_details["data"][2]
  document.getElementById("descr_field").value=account_details["data"][4]
}

