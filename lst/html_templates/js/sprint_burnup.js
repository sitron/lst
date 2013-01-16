var BurnupChart = function() {
    function create(data, commitedValues) {
        data.unshift({'storyPoints': 0, 'manDays': 0, 'date': '0'});
        var key = function(d) {return d.manDays},
            dataToDates = function(d) {return d.date},
            dates = data.map(dataToDates),
            height = 800,
            width = 800,
            maxDate = new Date(d3.max(dates)),
            endDate = new Date(sprint.endDate),
            dateFormat = d3.time.format('%a %d'),
            dateLongFormat = d3.time.format('%Y-%m-%d');

        var allDates,
            xScale,
            chart,
            xAxis,
            axisContainer,
            result,
            biggestRatio;

        // to show a nicer graph we draw all days till the end of the sprint
        // not only past ones
        allDates = dates.slice(0);
        if (maxDate < endDate) {
            while (maxDate < endDate) {
                maxDate.setDate(maxDate.getDate() + 1);
                if (maxDate.getDay() != 6 && maxDate.getDay() != 0) {
                    allDates.push(dateLongFormat(maxDate));
                }
            }
        }

        xScale = d3.scale.ordinal()
            .domain(allDates)
            .rangePoints([0, width]);

        chart = d3.select('#graph').append('svg')
            .attr('class', 'chart')
            .attr('width', width + 100)
            .attr('height', height + 100)
            .append('g')
            .attr('transform', 'translate(40, 20)');

        // create axis container and draw x axis
        xAxis = d3.svg.axis()
            .scale(xScale)
            .tickFormat(function(d) {
                if (d == 0) return d;
                var date = new Date(d);
                return dateFormat(date);
            })
            .orient('bottom');

        axisContainer = chart.append('g')
            .attr('class', 'axis-container');

        axisContainer.append('g')
            .attr('class', 'axis')
            .attr('transform', 'translate(0, ' + height + ')')
            .call(xAxis);


        // final results and biggestRatio calculation
        // biggest ratio used if more than 100% was achieved
        // (in either BV, SP, MD)
        result = data[data.length - 1];
        biggestRatio =
            Math.max(
                Math.max(
                    (result.manDays / commitedValues.manDays),
                    (result.storyPoints / commitedValues.storyPoints)
                ),
                (result.businessValue / commitedValues.businessValue)
            );

        _addGraph(
            data,
            'manDays',
            'man-days',
            chart,
            'left',
            axisContainer,
            height,
            xScale,
            0,
            commitedValues,
            biggestRatio);
        _addGraph(
            data,
            'storyPoints',
            'story-points',
            chart,
            'left',
            axisContainer,
            height,
            xScale,
            width,
            commitedValues,
            biggestRatio);
        _addGraph(
            data,
            'businessValue',
            'business-value',
            chart,
            'right',
            axisContainer,
            height,
            xScale,
            width,
            commitedValues,
            biggestRatio);
    };

    /**
     * Add a new line graph and corresponding y axis
     *
     * @param {Array}    data (contains all data, for all graphs).
     * @param {String}   prop data property to use for graph population.
     * @param {String}   name graph name (used for css classes).
     * @param {Svg}      chart svg container for chart.
     * @param {String}   orientation axis labels orientation.
     * @param {Svg}      axisContainer svg container for axis.
     * @param {Integer}  height of the graph (to create scale).
     * @param {Function} xScale mapping on x axis.
     * @param {Number}   position x position of the axis.
     * @param {Object}   object commited values.
     * @param {Number}   biggestRatio ratio of the most successful axe
     *                   (only important if sprint result > 100%).
     */
    function _addGraph(
            data,
            prop,
            name,
            chart,
            orientation,
            axisContainer,
            height,
            xScale,
            position,
            commitedValues,
            biggestRatio) {

        var max = biggestRatio > 1 ?
                biggestRatio * commitedValues[prop] : commitedValues[prop],
            yScale,
            graph,
            yAxis;

        yScale = d3.scale.linear()
            .domain([0, max])
            .range([height, '0']);

        graph = chart.append('svg:g')
            .attr('class', name + '-graph');

        graph.append('path')
            .datum(data)
            .attr('class', 'chart-line ' + name)
            .attr('d', d3.svg.line()
                .x(function(d) { return xScale(d.date); })
                .y(function(d) { return yScale(d[prop] || 0); })
            );

        graph.selectAll('.point')
            .data(data)
            .enter().append('svg:circle')
            .attr('class', 'point')
            .attr('r', 4)
            .attr('cx', function(d) {return xScale(d.date);})
            .attr('cy', function(d) {return yScale(d[prop] || 0);});

        yAxis = d3.svg.axis()
            .scale(yScale)
            .orient(orientation);

        axisContainer.append('g')
            .attr('class', 'axis ' + name)
            .attr('transform', 'translate(' + position + ', 0)')
            .call(yAxis);
    }

    return {'create': create};
}();


var PieChart = function() {
    function create(result, selector, size) {
        var dim = size || 150,
            data,
            vis,
            arc,
            pie,
            arcs;

        data = [Math.min(100, result), Math.max(0, (100 - result))];

        vis = d3.select(selector)
            .append('svg:svg')
            .data([data])
                .attr('width', dim)
                .attr('height', dim)
            .append('svg:g')
                .attr('transform',
                        'translate(' + (dim / 2) + ',' + (dim / 2) + ')'
                );

        arc = d3.svg.arc()
            .outerRadius(dim / 2);

        pie = d3.layout.pie()
            .sort(null) // to not sort pie slices by asc values (default)
            .value(function(d) { return d; });

        arcs = vis.selectAll('g.slice')
            .data(pie)
            .enter()
                .append('svg:g')
                    .attr('class', 'slice');

        arcs.append('svg:path')
            .attr('class', function(d, i) {return 'slice-' + i;})
            .attr('d', arc);
    }

    function displayResult(result, selector) {
        $(selector).text(result + ' %');
    }


    return {
        'create': create,
        'displayResult': displayResult
    };
}();

var SprintVelocity = function() {
    function display(selector, spResult, mdResult, spCommited, mdCommited) {
        $(selector).text(
            (spResult / mdResult).toFixed(2) +
            ' / ' +
            (spCommited / mdCommited)
                .toFixed(2)
        );
    }

    return {'display': display};
}();

$(function() {
    var last,
        mdResult,
        spResult,
        bvResult;

    last = data[data.length - 1];
    mdResult = Math.round(
        (last.manDays / commitedValues.manDays) * 100
    );
    spResult = Math.round(
        (last.storyPoints / commitedValues.storyPoints) * 100
    );
    bvResult = Math.round(
        (last.businessValue / commitedValues.businessValue) * 100
    );

    // create the main chart
    BurnupChart.create(data, commitedValues);

    // create the 3 result pie charts on top
    PieChart.create(mdResult, '#graph-results .man-days .chart');
    PieChart.displayResult(mdResult, '#graph-results .man-days .value');
    PieChart.create(spResult, '#graph-results .story-points .chart');
    PieChart.displayResult(mdResult, '#graph-results .story-points .value');
    PieChart.create(bvResult, '#graph-results .business-value .chart');
    PieChart.displayResult(mdResult, '#graph-results .business-value .value');

    // display velocity on top
    SprintVelocity.display(
        '#graph-results .velocity .value',
        spResult,
        mdResult,
        commitedValues.storyPoints,
        commitedValues.manDays
    );
});

