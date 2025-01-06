function addMinion() {
  fetch('api/get_minions')
    .then(response => response.json())
    .then(data => {
      const elements = document.getElementsByClassName('main-block');
      elements[0].innerHTML = JSON.stringify(data);
      console.log('data fetched correcctly');
      console.log(data);
    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
}

addMinion();
