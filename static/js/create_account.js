
  
const accountField = document.getElementById("account_name")
const InterestField = document.getElementById("Interest")
const notesField = document.getElementById("Details")
function SubmitData(){
  post(window.location.href,{accountName:accountField.value,accountNotes:notesField.value,accountInterest:InterestField.value})
}

