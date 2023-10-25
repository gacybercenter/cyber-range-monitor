fetch('/api/tree_data')
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById('tree');
        const nodes = [];
        const links = [];

        data.forEach(node => {
            if (node.identifier && !node.primaryConnectionIdentifier) {
                nodes.push(node);
            }
        });

        // data.forEach(node => {
        //     if (node.identifier) {
        //         nodes.push(node);
        //     }
        // });

        nodes.forEach(node => {
            if (node.parentIdentifier) {
                let parent = nodes.find(n => n.identifier === node.parentIdentifier);
                links.push({
                    source: parent,
                    target: node
                });
            }
            // else if (node.primaryConnectionIdentifier) {
            //     let parent = nodes.find(n => n.identifier === node.primaryConnectionIdentifier);
            //     links.push({
            //         source: parent,
            //         target: node
            //     });
            // }
        });

        function countDepth(node) {
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

        nodes.forEach(node => {
            node.depth = countDepth(node);
            node.size = 1.5 ** node.depth + 1;
        });

        const width = container.clientWidth;
        const height = container.clientHeight;

        const colors = {
            '1': 'rgb(000, 000, 000)',
            '2': 'rgb(192, 000, 000)',
            '3': 'rgb(000, 192, 000)',
            '4': 'rgb(000, 000, 192)',
            '5': 'rgb(255, 255, 255)'
        }

        const drag = d3.drag()
            .on("start", dragStarted)
            .on("drag", dragged)
            .on("end", dragEnded);

        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .call(d3.zoom().on('zoom', (event) => {
                svg.attr('transform', event.transform)
            }))
            .append('g');

        const link = svg.selectAll('line')
            .data(links)
            .enter()
            .append('line')
            .attr('stroke', 'black');

        const node = svg.selectAll('circle')
            .data(nodes)
            .enter()
            .append('circle')
            .attr('r', d => d.size)
            .attr("fill", d => colors[d.depth])
            .call(drag);

        const title = svg.append('g')
            .selectAll('text')
            .data(nodes)
            .join('text')
            .text(d => d.name)
            .attr('dy', d => d.size * 1.5)
            .style('font-size', d => d.size / 2)
            .attr('fill', 'white')
            .attr('text-anchor', 'middle')
            .style('font-family', "Verdana, Helvetica, Sans-Serif")
            .style('pointer-events', 'none');

        const connections = svg.append('g')
            .selectAll('text')
            .data(nodes.filter(d => d.protocol !== undefined))
            .join('text')
            .text(d => d.activeConnections)
            .attr('dy', d => d.size / 2)
            .style('font-size', d => d.size * 1.5)
            .attr('fill', 'white')
            .attr('text-anchor', 'middle')
            .style('font-family', "Verdana, Helvetica, Sans-Serif")
            .style('pointer-events', 'none');

        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id((d, i) => i))
            .force('charge', d3.forceManyBody()
                .strength(d => d.size * -4))
            .force('center', d3.forceCenter(width / 2, height / 2));

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
                .attr("y", d => d.y);
        });


        function dragStarted(event, d) {
            if (!event.active) {
                simulation.alphaTarget(0.3).restart();
            }
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragEnded(event, d) {
            if (!event.active) {
                simulation.alphaTarget(0);
            }
            d.fx = null;
            d.fy = null;
        }

    });
