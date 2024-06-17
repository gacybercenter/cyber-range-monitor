function updateActiveConns() {
    fetch('/api/active_connections')
        .then(response => response.json())
        .then(data => {
            const connList = document.getElementById('active-conns-container');
            connList.innerHTML = '';
            const projectMap = new Map();

            // Group connections by project
            data.forEach(conn => {
                const project = conn.project || "Unassigned";
                if (!projectMap.has(project)) {
                    projectMap.set(project, []);
                }
                projectMap.get(project).push(conn);
            });

            // Create table for each project
            projectMap.forEach((conns, project) => {
                const projectDiv = document.createElement('div');
                projectDiv.classList.add('project-section');

                const projectTitle = document.createElement('h2');
                projectTitle.textContent = `Project: ${project}`;
                projectDiv.appendChild(projectTitle);

                const table = document.createElement('table');
                table.classList.add('connections-table');

                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');
                const headers = ['Instance'];
                headers.forEach(headerText => {
                    const th = document.createElement('th');
                    th.textContent = headerText;
                    headerRow.appendChild(th);
                });
                thead.appendChild(headerRow);
                table.appendChild(thead);

                const tbody = document.createElement('tbody');
                conns.forEach(conn => {
                    const row = document.createElement('tr');
                    const instanceCell = document.createElement('td');
                    instanceCell.textContent = conn.instance;
                    row.appendChild(instanceCell);
                    tbody.appendChild(row);
                });
                table.appendChild(tbody);

                projectDiv.appendChild(table);
                connList.appendChild(projectDiv);
            });
        })
        .catch(error => {
            console.error('Error fetching connection data:', error);
        });
}

updateActiveConns();
setInterval(updateActiveConns, 10000);
