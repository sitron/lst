var that = this;

function mapToData() {
    data.unshift({'storyPoints': 0, 'manDays': 0, 'date': '0'});
    var key = function(d) {return d.manDays};
    var dataToDates = function(d) {return d.date};
    var dates = data.map(dataToDates);
    var height = 400;
    var width = 800;

    var maxDate = new Date(d3.max(dates));
    var endDate = new Date(sprint.endDate);
    var dateFormat = d3.time.format('%a %d');
    var dateLongFormat = d3.time.format('%Y-%m-%d');

    // to show a nicer graph we draw the day till the end of the sprint
    // not only achieved ones
    var allDates = dates.slice(0);
    if (maxDate < endDate) {
        while (maxDate < endDate) {
            maxDate.setDate(maxDate.getDate() + 1);
            if (maxDate.getDay() != 6 && maxDate.getDay() != 0) {
                allDates.push(dateLongFormat(maxDate));
            }
        }
    }

    var xScale = d3.scale.ordinal()
        .domain(allDates)
        .rangePoints([0, width]);

    var chart = d3.select('#graph').append('svg')
        .attr('class', 'chart')
        .attr('width', width + 100)
        .attr('height', height + 100)
        .append('g')
        .attr('transform', 'translate(40, 20)');

    // axis
    var xAxis = d3.svg.axis()
        .scale(xScale)
        .tickFormat(function(d) {
            if (d == 0) return d;
            var date = new Date(d);
            return dateFormat(date);
        })
        .orient('bottom');

    var axisContainer = chart.append('g')
        .attr('class', 'axis-container');

    axisContainer.append('g')
        .attr('class', 'axis')
        .attr('transform', 'translate(0, ' + height + ')')
        .call(xAxis);


    // add graphs
    var result = data[data.length - 1];
    var biggestRatio =
        Math.max(
            Math.max(
                (result.manDays / commitedValues.manDays),
                (result.storyPoints / commitedValues.storyPoints)
            ),
            (result.businessValue / commitedValues.businessValue)
        );

    addGraph(
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
    addGraph(
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
    addGraph(
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
}

/**
 * Add a new graph
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
 * @param {Object}  object commited values.
 * @param {Number}   biggestRatio ratio of the most successful axe
 *                   (only important if sprint result > 100%).
 */
function addGraph(
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

    var max = biggestRatio > 1 ? biggestRatio * commitedValues[prop] : commitedValues[prop];

    var yScale = d3.scale.linear()
        .domain([0, max])
        .range([height, '0']);

    var graph = chart.append('svg:g')
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

    var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient(orientation);

    axisContainer.append('g')
        .attr('class', 'axis ' + name)
        .attr('transform', 'translate(' + position + ', 0)')
        .call(yAxis);
}

$(function() {
    that.mapToData();

    var last = data[data.length - 1];
    $('#graph-results .man-days').text(
        Math.round((last.manDays / commitedValues.manDays) * 100) + '%');
    $('#graph-results .story-points').text(
        Math.round((last.storyPoints / commitedValues.storyPoints) * 100) + '%');
    $('#graph-results .business-value').text(
        Math.round((last.businessValue / commitedValues.businessValue) * 100) + '%');

    $('#story-points-toggle').click(function() {
        var storyPointGraph = $('.story-points-graph'),
            storyPointAxis = $('.axis.story-points');

        if (storyPointGraph.css('display') != 'none') {
            storyPointAxis.hide();
            storyPointGraph.hide();
        } else {
            storyPointAxis.show();
            storyPointGraph.show();
        }
    });
});

