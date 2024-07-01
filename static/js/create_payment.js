
function SubmitData(){
  paymentName = document.getElementById("paymentName").value
  amountField = document.getElementById("Amount").value;
  ChildField = document.getElementById("child").value;
  accountField = document.getElementById("account").value;
  FrequencyField = document.getElementById("Frequency").value;
  notesField = document.getElementById("notes").value;
  post(window.location.href,{paymentName:paymentName,amount:amountField,childId:ChildField,accountId:accountField,frequency:FrequencyField,notes:notesField})
}
