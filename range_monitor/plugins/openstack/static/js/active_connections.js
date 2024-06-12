function updateActiveConns() {
   fetch('/api/openstack/active_connections')
        .then(response => response.json())
        .then(data => {
            const connList = document.getElementById('active-conns-container');
            connList.innerHTML = '';
            const projectMap = new Map();

            // Group connections by project
            data.conns.forEach(conn => {
                const project = conn.project || "Unassigned";
                if (!projectMap.has(project)) {
                    projectMap.set(project, []);
                }
                projectMap.get(project).push(conn);
            });

            // Create columns for each project 
            // TODO: ADD MULTIPLE PROJECTS
            projectMap.forEach((conns, project) => {
                const column = document.createElement('div');
                column.classList.add('column');
                column.innerHTML = `<h2>Project: ${project}</h2>`;
                const ul = document.createElement('ul');
                ul.classList.add('connections');
                
                // Add connections to the current prefix's column
                conns.forEach(conn => {
                    const connItem = document.createElement('li');
                    connItem.textContent = `${conn.instance} - ${conn.username}`;
                    ul.appendChild(connItem);
                });

                column.appendChild(ul);
                connList.appendChild(column);
            });
        })
        .catch(error => {
            console.error('Error fetching connection data:', error);
        });
}

updateActiveConns();
setInterval(updateActiveConns, 10000);