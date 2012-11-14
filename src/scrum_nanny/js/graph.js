var that = this;
function mapToData() {
    console.log('map');
    console.log(data);

    data.unshift({'storyPoints': 0, 'manDays': 0, 'date': '0.0'});
    var key = function(d) {return d.manDays};
    var dataToDates = function(d) {return d.date};
    var dates = data.map(dataToDates);
    var maxManDays = d3.max(data, function(d) {return d.manDays});
    var maxStoryPoints = d3.max(data, function(d) {return d.storyPoints});
    var max = d3.max([maxManDays, maxStoryPoints]);
    console.log(max);
    var height = 400;
    var width = 400;
    var yManDays = d3.scale.linear()
        .domain([0, maxManDays])
        .range([height, '0']);
    var yStoryPoints = d3.scale.linear()
        .domain([0, maxStoryPoints])
        .range([height, '0']);

    var x = d3.scale.ordinal()
        .domain(dates)
        .rangePoints([0, width]);

    var yticker = d3.scale.linear()
        .domain([0, data.length])
        .range([width, '0']);

    var chart = d3.select('body').append('svg')
        .attr('class', 'chart')
        .attr('width', 500)
        .attr('height', 500)
        .append('g')
        .attr('transform', 'translate(40, 20)');

    var manDaysGraph = chart.append('svg:g')
        .attr('class', 'man-days-graph');
    var storyPointsGraph = chart.append('svg:g')
        .attr('class', 'story-points-graph');

    // man days graph
    manDaysGraph.append('path')
        .datum(data)
        .attr('class', 'chart-line man-days')
        .attr('d', d3.svg.line()
            .x(function(d) { return x(d.date); })
            .y(function(d) { return yManDays(d.manDays || 0); })
        );

    manDaysGraph.selectAll('.point')
        .data(data)
        .enter().append('svg:circle')
        .attr('class', 'point')
        .attr('r', 4)
        .attr('cx', function(d) {return x(d.date);})
        .attr('cy', function(d) {return yManDays(d.manDays || 0);});

    // story points graph
    storyPointsGraph.append('path')
        .datum(data)
        .attr('class', 'chart-line story-points')
        .attr('d', d3.svg.line()
            .x(function(d) { return x(d.date); })
            .y(function(d) { return yStoryPoints(d.storyPoints || 0); })
        );

    storyPointsGraph.selectAll('.point')
        .data(data)
        .enter().append('svg:circle')
        .attr('class', 'point')
        .attr('r', 4)
        .attr('cx', function(d) {return x(d.date);})
        .attr('cy', function(d) {return yStoryPoints(d.storyPoints || 0);});

    // axis
    var xAxis = d3.svg.axis()
        .scale(x)
        .orient('bottom');

    var yAxisManDays = d3.svg.axis()
        .scale(yManDays)
        .orient('left');
    var yAxisStoryPoints = d3.svg.axis()
        .scale(yStoryPoints)
        .orient('right');
    var yAxisBusinessValue = d3.svg.axis()
        .scale(yStoryPoints)
        .orient('left');

    var axisContainer = chart.append('g')
        .attr('class', 'axis-container');

    axisContainer.append('g')
        .attr('class', 'axis')
        .attr('transform', 'translate(0, ' + height + ')')
        .call(xAxis);

    axisContainer.append('g')
        .attr('class', 'axis man-days')
        .attr('transform', 'translate(0, 0)')
        .call(yAxisManDays);

    axisContainer.append('g')
        .attr('class', 'axis story-points')
        .attr('transform', 'translate(' + (width + 30) + ', 0)')
        .call(yAxisStoryPoints);

    axisContainer.append('g')
        .attr('class', 'axis business-value')
        .attr('transform', 'translate(' + (width + 30) + ', 0)')
        .call(yAxisBusinessValue);
}

// data = data
// name = man-days
// chart = chart
// orientation = left
// axisContainer
function addGraph(data, name, chart, orientation, axisContainer) {
    var maxManDays = d3.max(data, function(d) {return d.manDays});

    var yManDays = d3.scale.linear()
        .domain([0, maxManDays])
        .range([height, '0']);

    var manDaysGraph = chart.append('svg:g')
        .attr('class', name + '-graph');

    manDaysGraph.append('path')
        .datum(data)
        .attr('class', 'chart-line ' + name)
        .attr('d', d3.svg.line()
            .x(function(d) { return x(d.date); })
            .y(function(d) { return yManDays(d.manDays || 0); })
        );

    manDaysGraph.selectAll('.point')
        .data(data)
        .enter().append('svg:circle')
        .attr('class', 'point')
        .attr('r', 4)
        .attr('cx', function(d) {return x(d.date);})
        .attr('cy', function(d) {return yManDays(d.manDays || 0);});

    var yAxisManDays = d3.svg.axis()
        .scale(yManDays)
        .orient(orientation);

    axisContainer.append('g')
        .attr('class', 'axis ' + name)
        .attr('transform', 'translate(0, 0)')
        .call(yAxisManDays);
}

$(function() {
    that.mapToData();
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

