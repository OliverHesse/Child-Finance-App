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
function stripped_href(){
  //gets me the base url
  //only needed whilst on replit
  url = window.location.href;
  curr_url = window.location.href.split("/");
  //+2 because of the removed //
  body_length = curr_url[0].length+curr_url[2].length+2;
  base = url.substring(0,body_length);

  return base
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
//quicksort algorithm modifed to work with 2d arrays
function partition(array,left,right,index){

  pivot=Math.floor(Math.random() * (right - left + 1) + left);

  let pivotValue = array[pivot]
  array[pivot] = array[right]
  array[right] = pivotValue
  let storePosition = left
  for(let i = left; i <=right; i++){
    if(array[i][index]<pivotValue[index]){
      let temp = array[storePosition]
      array[storePosition] = array[i]
      array[i] = temp
      storePosition += 1
    }
  }
  let temp = array[storePosition]
  array[storePosition] = array[right]
  array[right] = temp
  return storePosition
}
function quicksort(array,left,right,index){
  if(left<right){
    let p = partition(array,left,right,index)
    quicksort(array,left,p-1,index)//lower values
    quicksort(array,p+1,right,index)//higher values
  }
}

