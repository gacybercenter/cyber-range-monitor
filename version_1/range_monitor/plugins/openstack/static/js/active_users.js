function updateActiveConns() {
    fetch('api/users_data')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('active-users-container');
            // Clear the container before adding new data
            container.innerHTML = '';

            for (const [org, users] of Object.entries(data)) {
                const column = document.createElement('div');
                column.classList.add('column');
                column.innerHTML = `<h2>${org}</h2>`;
                const ul = document.createElement('ul');
                ul.classList.add('connections');

                // Loop through users array and append list items to the 'ul'
                for (const user of users) {
                    const li = document.createElement('li');
                    li.textContent = user;
                    ul.appendChild(li);
                }

                column.appendChild(ul);
                container.appendChild(column);
            }
        });
}

// Initial call to populate the data
updateActiveConns();

// Set interval to refresh the data every 5 seconds
setInterval(updateActiveConns, 5000);