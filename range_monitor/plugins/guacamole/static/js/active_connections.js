function updateActiveConns() {
    fetch('api/conns_data')
        .then(response => response.json())
        .then(data => {
            const connList = document.getElementById('active-conns-container');
            connList.innerHTML = '';
            const prefixMap = new Map();

            // Group connections by prefix
            data.conns.forEach(conn => {
                const prefix = conn.connection.split('.')[0] || "None";
                if (!prefixMap.has(prefix)) {
                    prefixMap.set(prefix, []);
                }
                prefixMap.get(prefix).push(conn);
            });

            // Create columns for each prefix
            prefixMap.forEach((conns, prefix) => {
                const column = document.createElement('div');
                column.classList.add('column');
                column.innerHTML = `<h2>${prefix}</h2>`;
                const ul = document.createElement('ul');
                ul.classList.add('connections');
                
                // Add connections to the current prefix's column
                conns.forEach(conn => {
                    const connItem = document.createElement('li');
                    connItem.textContent = `- ${conn.connection} (${conn.username})`;
                    ul.appendChild(connItem);
                });

                column.appendChild(ul);
                connList.appendChild(column);
            });
        });
}

updateActiveConns();
setInterval(updateActiveConns, 5000);