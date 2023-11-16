let refresh = true;
let inactive = true;
let selectedIdentifier = null;
let updateID = null;

const container = document.getElementById('topology');
const nodeDataContainer = document.getElementById('node-data');

const connectButton = document.getElementById('connect-button');
const killButton = document.getElementById('kill-button');
const timelineButton = document.getElementById('timeline-button');

const toggleRefreshButton = document.getElementById('toggle-refresh-button');
const toggleInactiveButton = document.getElementById('toggle-inactive-button');

connectButton.addEventListener('click', function () {
    if (!selectedIdentifier) {
        alert('Please select a node first!');
        return;
    }
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/guacamole/connect-to-node', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            var url = response.url;
            window.open(url, '_blank');
            console.log(response);
        } else if (xhr.readyState === XMLHttpRequest.DONE) {
            alert(xhr.responseText);
        }
    };
    var data = JSON.stringify({ identifier: selectedIdentifier });
    xhr.send(data);
});

killButton.addEventListener('click', function () {
    if (!selectedIdentifier) {
        alert('Please select a node first!');
        return;
    }
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/guacamole/kill-connections', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            console.log(response);
        } else if (xhr.readyState === XMLHttpRequest.DONE) {
            alert(xhr.responseText);
        }
    };
    var data = JSON.stringify({ identifier: selectedIdentifier });
    xhr.send(data);
});

timelineButton.addEventListener('click', function () {
    if (!selectedIdentifier) {
        alert('Please select a node first!');
        return;
    }
    window.location.href = selectedIdentifier + '/connection_timeline';
});

function toggleRefresh() {
    refresh = !refresh;
    toggleRefreshButton.textContent = refresh ? 'Disable Refresh' : 'Enable Refresh';

    if (refresh) {
        updateTopology();
        updateID = setInterval(updateTopology, 5000);
    } else {
        clearInterval(updateID);
        updateID = null;
    }
}

function toggleInactive() {
    inactive = !inactive;
    toggleInactiveButton.textContent = inactive ? 'Disable Inactive' : 'Enable Inactive';

    updateTopology(true);

    svg.selectAll('circle').classed('selected', false);
    nodeDataContainer.innerHTML = null;
    selectedIdentifier = null;

    if (refresh) {
        clearInterval(updateID);
        updateID = setInterval(updateTopology, 5000);
    }
}

const width = container.clientWidth;
const height = container.clientHeight;
const colors = {
    '1': 'rgb(000, 000, 000)',
    '2': 'rgb(192, 000, 000)',
    '3': 'rgb(000, 192, 000)',
    '4': 'rgb(000, 000, 192)',
    '5': 'rgb(255, 255, 255)'
}

const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .call(d3.zoom().on('zoom', (event) => {
        svg.attr('transform', event.transform)
    }))
    .append('g');

const simulation = d3.forceSimulation()
    .force('link', d3.forceLink().id((d) => d.identifier))
    .force('charge', d3.forceManyBody()
        .strength(d => d.size * -4))
    .force('center', d3.forceCenter(width / 2, height / 2));

const drag = d3.drag()
    .on("start", dragStarted)
    .on("drag", dragged)
    .on("end", dragEnded);

let link = svg.append('g')
    .attr('stroke', 'black')
    .attr('stroke-width', 1)
    .selectAll('line');

let node = svg.append('g')
    .selectAll('circle');

let title = svg.append('g')
    .attr('fill', 'white')
    .attr('text-anchor', 'middle')
    .style('font-family', "Verdana, Helvetica, Sans-Serif")
    .style('pointer-events', 'none')
    .selectAll('text');

let connections = svg.append('g')
    .attr('fill', 'white')
    .attr('text-anchor', 'middle')
    .style('font-family', "Verdana, Helvetica, Sans-Serif")
    .style('pointer-events', 'none')
    .selectAll('text');

/**
 * Updates the topology by fetching data from the '/api/topology_data' endpoint and
 * rendering it as a graph. If the 'start' parameter is set to true, the simulation will
 * start immediately, otherwise it will start with a low alpha value.
 *
 * @param {boolean} [start=false] - Indicates whether the simulation just started.
 */
function updateTopology(start = false) {
    fetch('api/topology_data')
        .then(response => response.json())
        .then(data => {

            if (!data) {
                return;
            }

            const nodes = [{
                name: 'ROOT',
                identifier: 'ROOT'
            }];
            const links = [];

            data.forEach(node => {
                if (node.identifier) {
                    if (inactive) {
                        nodes.push(node);
                    } else if (node.type || node.activeConnections > 0) {
                        nodes.push(node);
                    }
                }
            });

            nodes.forEach(node => {
                node.data = removeNullValues(node);
                node.weight = countWeight(node);
                node.size = 1.5 ** node.weight + 1;
                if (node.parentIdentifier) {
                    let parent = nodes.find(n => n.identifier === node.parentIdentifier);
                    if (parent) {
                        links.push({
                            source: parent,
                            target: node
                        });
                    }
                }
            });

            link = link.data(links)
                .join('line');

            const previousNodePositions = new Map(
                node.data().map(
                    d => [d.identifier, { x: d.x, y: d.y }]
                )
            );

            node = node.data(nodes)
                .join('circle')
                .attr('r', d => d.size)
                .attr('fill', d => colors[d.weight])
                .call(drag)
                .on('click', function (d) {
                    svg.selectAll('circle').classed('selected', false);
                    d3.select(this).classed('selected', true);

                    let nodeData = d.target.__data__.data;
                    let htmlData = convertToHtml(nodeData);
                    nodeDataContainer.innerHTML = htmlData;

                    if (nodeData.protocol) {
                        selectedIdentifier = nodeData.identifier;
                    }
                    else {
                        selectedIdentifier = null;
                    }

                });

            title = title.data(nodes)
                .join('text')
                .text(d => d.name || 'Unnamed Node')
                .attr('dy', d => d.size * 1.5)
                .style('font-size', d => d.size / 2)

            connections = connections.data(nodes.filter(d => d.protocol !== undefined))
                .join('text')
                .text(d => d.activeConnections)
                .attr('dy', d => d.size / 2)
                .style('font-size', d => d.size * 1.5);

            simulation.nodes(nodes)

            let isNewNodes = false;
            nodes.forEach(node => {
                const previousPosition = previousNodePositions.get(node.identifier);
                if (previousPosition) {
                    Object.assign(node, previousPosition);
                } else {
                    isNewNodes = true;
                }
            });
            simulation.force('link').links(links);
            if (start === true) {
                simulation.alpha(1).restart();
            } else if (isNewNodes) {
                simulation.alpha(0.1).restart();
            } else {
                simulation.alpha(0).restart();
            }
            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);

                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);

                title
                    .attr("x", d => d.x)
                    .attr("y", d => d.y);

                connections
                    .attr("x", d => d.x)
                    .attr("y", d => d.y)
            });
        });
}

updateTopology(true);
updateID = setInterval(updateTopology, 5000);

/**
 * Handles the start of a drag event.
 *
 * @param {Event} event - the drag event
 * @param {Object} d - the data associated with the dragged element
 */
function dragStarted(event, d) {
    if (!event.active) {
        simulation.alphaTarget(0.1).restart();
    }
    d.fx = d.x;
    d.fy = d.y;

    if (updateID) {
        clearInterval(updateID);
    }
}

/**
 * Updates the position of a dragged element.
 *
 * @param {event} event - the event object representing the drag event
 * @param {d} d - the data object associated with the dragged element
 */
function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

/**
 * Handles the event when dragging ends.
 *
 * @param {Object} event - The event object.
 * @param {Object} d - The data object.
 */
function dragEnded(event, d) {
    if (!event.active) {
        simulation.alphaTarget(0);
    }
    d.fx = null;
    d.fy = null;
    if (refresh) {
        updateID = setInterval(updateTopology, 5000);
    }
}

/**
 * Removes null values from an object, including nested objects and arrays.
 *
 * @param {object} obj - The object to remove null values from.
 * @return {object} - The object with null values removed.
 */
function removeNullValues(obj) {
    let objCopy = JSON.parse(JSON.stringify(obj));              // Create a deep copy of the object

    for (let key in objCopy) {
        if (objCopy[key] === null || objCopy[key] === '') {
            delete objCopy[key];
        } else if (typeof objCopy[key] === 'object') {
            objCopy[key] = removeNullValues(objCopy[key]);      // Recursively call the function for nested objects
            if (Array.isArray(objCopy[key])) {
                objCopy[key] = objCopy[key].filter(Boolean);    // Remove null and empty entries from arrays
            }
        }
    }

    return objCopy;
}


/**
 * Converts an object into a formatted string representation.
 *
 * @param {Object} obj - The object to be converted.
 * @param {number} indent - The number of spaces to indent each level of the string representation.
 *                          Default is 0.
 * @return {string} The formatted string representation of the object.
 */
function convertToHtml(obj) {
    if (typeof obj !== 'object') {
        return obj;
    }
    let html;
    if (obj.users) {
        html = `<strong>${obj.name || ''}</strong><br>(${obj.users || ''})<br><br>`;
    }
    else {
        html = `<strong>${obj.name || ''}</strong><br><br>`;
    }

    /**
     * Converts an object into a formatted string representation.
     *
     * @param {Object} obj - The object to be converted.
     * @param {number} indent - The number of spaces to indent each level of the string representation.
     *                          Default is 0.
     */
    function convert(obj, indent = 0) {
        const keys = Object.keys(obj);
        for (const key of keys) {
            const value = obj[key];
            const dashIndent = '\u00A0\u00A0'.repeat(indent);
            if (typeof value === 'object' && value !== null) {
                html += `${dashIndent}${key}:\n`;
                convert(value, indent + 1);
            } else {
                const convertedValue = key === 'lastActive' ? new Date(value).toLocaleString() : value;
                html += `${dashIndent}${key}: ${convertedValue}\n`;
            }
        }
    }

    convert(obj);

    return html.replace(/\n/g, '<br>').replace(/\u00A0/g, '&nbsp;');
}

/**
 * Calculates the weight of a given node based on its properties.
 *
 * @param {Object} node - The node object to calculate the weight for.
 * @return {number} The weight of the node.
 */
function countWeight(node) {
    if (node.identifier === 'ROOT') {
        return 5;
    }
    if (node.type) {
        return 4;
    }
    if (node.activeConnections > 0) {
        return 3;
    }
    if (node.protocol) {
        return 2;
    }
    if (node.primaryConnectionIdentifier) {
        return 1;
    }
    return 0;
}
