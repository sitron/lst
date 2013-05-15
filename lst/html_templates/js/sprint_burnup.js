/**
 * Manage data for charts (pies, lines) and results
 *
 * @return {Object} public methods.
 */
var DataManager = function() {
    var fullData,
        commitedValues;

    /**
     * Set data
     *
     * @param {array} data Full list of data objects.
     */
    function setData(data) {
        fullData = data;
    }

    /**
     * Get full data list
     *
     * @return {Array} full data list.
     */
    function getData() {
        return fullData;
    }

    /**
     * Set commited values
     *
     * @param {object} values Object of commited values.
     */
    function setCommitedValues(values) {
        commitedValues = values;
    }

    /**
     * Get commited values
     *
     * @return {Object} commited values.
     */
    function getCommitedValues() {
        return commitedValues;
    }

    /**
     * Return an array with only data for the corresponding 'valueName'
     * Needed as we don't want all the graphs to stop at the same x point
     *
     * @param {string} valueName Name of the value to map.
     * @return {array} list of data objects with only the specific values.
     */
    function getDataPerGraph(valueName) {
        specificData = [];
        for (var i = 0; i < fullData.length; i++) {
            if (typeof(fullData[i][valueName]) != 'undefined') {
                specificData.push({
                    'date': fullData[i].date,
                    'value': fullData[i][valueName]
                });
            }
        }
        return specificData;
    }

    /**
     * Get the max value for a specific graph
     *
     * @param {String} valueName Name of property to consider.
     * @return {Integer} max value.
     */
    function getMaxPerGraph(valueName) {
        var values = fullData.map(function(d) {
            return d[valueName];
        });
        return d3.max(values);
    }

    /**
     * Get the result for a specific graph
     *
     * @param {String} valueName Name of property to consider.
     * @return {Integer} result.
     */
    function getResultPerGraph(valueName) {
        return getMaxPerGraph(valueName) / commitedValues[valueName];
    }

    /**
     * Get the result in percent for a specific graph
     *
     * @param {String} valueName Name of property to consider.
     * @return {Integer} result in percent.
     */
    function getRoundedResultPerGraph(valueName) {
        return Math.round(getResultPerGraph(valueName) * 100);
    }

    /**
     * Extract date data from fullData
     *
     * @return {Array} List of dates.
     */
    function getDates() {
        return fullData.map(function(d) {
            return d.date;
        });
    }

    /**
     * Get biggest result ratio
     * only used if more than 100% achieved
     *
     * @return {number} best result.
     */
    function getBiggestRatio() {
        var biggestRatio =
            Math.max(
                Math.max(
                    getResultPerGraph('manDays'),
                    getResultPerGraph('storyPoints')
                ),
                getResultPerGraph('businessValue')
            );
        return biggestRatio;
    }

    /**
     * Get max date
     *
     * @return {date} max date.
     */
    function getMaxDate() {
        return new Date(d3.max(getDates()));
    }

    /**
     * check if specific graph is empty
     *
     * @param {String} valueName Name of property to consider.
     * @return {Boolean} true is empty.
     */
    function isGraphEmpty(valueName) {
        return getMaxPerGraph(valueName) == 0;
    }

    return {
        'setData': setData,
        'getData': getData,
        'setCommitedValues': setCommitedValues,
        'getCommitedValues': getCommitedValues,
        'getDataPerGraph': getDataPerGraph,
        'getMaxPerGraph': getMaxPerGraph,
        'getResultPerGraph': getResultPerGraph,
        'getRoundedResultPerGraph': getRoundedResultPerGraph,
        'getMaxDate': getMaxDate,
        'getDates': getDates,
        'getBiggestRatio': getBiggestRatio,
        'isGraphEmpty': isGraphEmpty
    };

}();

/**
 * BurnupChart Object
 *
 * @return {Object}  public methods.
 */
var BurnupChart = function() {

    /**
     * Create the chart
     */
    function create() {
        var key = function(d) {return d.manDays},
            height = 800,
            width = 800,
            endDate = new Date(sprint.endDate),
            graphEndDate = new Date(sprint.graphEndDate),
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
        allDates = DataManager.getDates().slice(0);
        if (DataManager.getMaxDate() < endDate) {
            maxDate = DataManager.getMaxDate();
            while (maxDate < endDate) {
                maxDate.setDate(maxDate.getDate() + 1);
                if (maxDate.getDay() != 6 && maxDate.getDay() != 0) {
                    allDates.push(dateLongFormat(maxDate));
                }
            }
        }
        // add x-axis origin
        allDates.unshift('0');

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

        var commitedValues = DataManager.getCommitedValues();

        // by default there is no commited result for "planned"
        if (!DataManager.isGraphEmpty('planned')) {
            commitedValues.planned = commitedValues.manDays;
        }

        var graphsProps = [
            {
                'prop': 'planned',
                'graphName': 'planned',
                'orientation': 'right',
                'position': undefined
            },
            {
                'prop': 'manDays',
                'graphName': 'man-days',
                'orientation': 'left',
                'position': 0
            },
            {
                'prop': 'storyPoints',
                'graphName': 'story-points',
                'orientation': 'left',
                'position': width
            },
            {
                'prop': 'businessValue',
                'graphName': 'business-value',
                'orientation': 'right',
                'position': width
            }
        ];

        // add all graphs
        for (var i = 0; i < graphsProps.length; i++) {
            if (!DataManager.isGraphEmpty(graphsProps[i].prop)) {
                _addGraph(
                    DataManager.getDataPerGraph(graphsProps[i].prop),
                    graphsProps[i].prop,
                    graphsProps[i].graphName,
                    chart,
                    graphsProps[i].orientation,
                    axisContainer,
                    height,
                    xScale,
                    graphsProps[i].position,
                    commitedValues,
                    DataManager.getBiggestRatio()
                );
            }
        }
    };

    /**
     * Add a new line graph and corresponding y axis
     *
     * @param {Array}    data List of data objects.
     * @param {String}   prop Data property to use for graph population.
     * @param {String}   name Graph name (used for css classes).
     * @param {Svg}      chart Svg container for chart.
     * @param {String}   orientation Axis labels orientation.
     * @param {Svg}      axisContainer Svg container for axis.
     * @param {Integer}  height Height of the graph (to create scale).
     * @param {Function} xScale xScale mapping on x axis.
     * @param {Number}   position x position of the axis.
     * @param {Object}   commitedValues commited values.
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

        var yScale,
            graph,
            yAxis,
            max = biggestRatio > 1 ?
                biggestRatio * commitedValues[prop] : commitedValues[prop];

        // add y-axis origin
        data.unshift({
            'value': 0,
            'date': '0'
        });

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
                .y(function(d) { return yScale(d.value || 0); })
            );

        graph.selectAll('.point')
            .data(data)
            .enter().append('svg:circle')
            .attr('class', 'point')
            .attr('r', 4)
            .attr('cx', function(d) {return xScale(d.date);})
            .attr('cy', function(d) {return yScale(d.value || 0);});

        if (position != undefined) {
            yAxis = d3.svg.axis()
                .scale(yScale)
                .orient(orientation);

            axisContainer.append('g')
                .attr('class', 'axis ' + name)
                .attr('transform', 'translate(' + position + ', 0)')
                .call(yAxis);
        }
    }

    return {
        'create': create
    };
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
    var mdResult,
        spResult,
        bvResult;

    DataManager.setData(data);
    DataManager.setCommitedValues(commitedValues);

    mdResult = DataManager.getRoundedResultPerGraph(
        'manDays'
    );
    spResult = DataManager.getRoundedResultPerGraph(
        'storyPoints'
    );
    bvResult = DataManager.getRoundedResultPerGraph(
        'businessValue'
    );

    // create the main chart
    BurnupChart.create();

    // create the 3 result pie charts on top
    PieChart.create(mdResult, '#graph-results .man-days .chart');
    PieChart.displayResult(mdResult, '#graph-results .man-days .value');
    PieChart.create(spResult, '#graph-results .story-points .chart');
    PieChart.displayResult(spResult, '#graph-results .story-points .value');
    PieChart.create(bvResult, '#graph-results .business-value .chart');
    PieChart.displayResult(bvResult, '#graph-results .business-value .value');

    // display velocity on top
    SprintVelocity.display(
        '#graph-results .velocity .value',
        spResult,
        mdResult,
        commitedValues.storyPoints,
        commitedValues.manDays
    );
});

