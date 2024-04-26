function updatePerformanceState() {
    fetch('api/performance_data')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementsById('performance-state-container');
            // Clear the container before adding new data
            container.innerHTML = '';

            for (const [instanceId, metrice] of Object.entries(data)) {
                const column = document.createElement('div');
                column.classList.add('column');
                column.innerHTML = `<h2>Instance: ${instanceId}</h2>`;
                const ul = document.createElement('ul');
                ul.classList.add('connections');

                // Loop through users array and append list items to the 'ul'
                for (const [metricName, metricValue] of Object.entries(metrice)) {
                    const li = document.createElement('li');
                    li.textContent = `${metricName}: ${metricValue}`;
                    ul.appendChild(li);
                }

                column.appendChild(ul);
                container.appendChild(column);
            }
        })
}_

updatePerformanceState();

setInterval(updatePerformanceState, 10000);