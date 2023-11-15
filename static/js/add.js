function buyMaterial(id) {
  const amount = document.getElementById(`amount-${id}`).value;
  const xhr = new XMLHttpRequest();
  xhr.open('POST', `/buy/${id}`);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onload = function() {
    if (xhr.status === 200) {
      console.log(xhr.responseText);
    } else {
      console.log('Error!');
    }
  };
  const data = JSON.stringify({ amount: amount });
  xhr.send(data);
}