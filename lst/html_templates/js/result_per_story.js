/**
 * Result per story graph Object
 *
 * @return {Object}  public methods.
 */
var ResultPerStoryChart = function() {

    /**
     * Create the chart
     */
    function create() {
        var key = function(d) {return d.manDays},
            height = 400,
            width = 800,
            barWidth = 25,
            xScale,
            chart,
            xAxis,
            axisContainer,
            result;

        console.log(data);

        storyIds = data.map(function(d) {return d.id;});
        storyBurnt = data.map(function(d) {return d.hours_burnt;});
        storyPlanned = data.map(function(d) {return d.hours_planned;});
        maxBurnt = d3.max(storyBurnt);
        maxPlanned = d3.max(storyPlanned);
        max = Math.max(maxBurnt, maxPlanned);

        xScale = d3.scale.ordinal()
            .domain(storyIds)
            .rangePoints([0, width], 1)

        yScale = d3.scale.linear()
            .domain([0, max])
            .range([height, '0'])

        chart = d3.select('#graph').append('svg')
            .attr('class', 'chart')
            .attr('width', width + 100)
            .attr('height', height + 100)
            .append('g')
            .attr('transform', 'translate(40, 20)');

        xAxis = d3.svg.axis()
            .scale(xScale)
            .orient('bottom');

        yAxis = d3.svg.axis()
            .scale(yScale)
            .orient('left');

        axisContainer = chart.append('g')
            .attr('class', 'axis-container');

        axisContainer.append('g')
            .attr('class', 'axis')
            .attr('transform', 'translate(0, ' + height + ')')
            .call(xAxis);

        axisContainer.append('g')
            .attr('class', 'axis')
            .call(yAxis);

        chart.selectAll('rect .burnt')
            .data(data)
            .enter().append('svg:rect')
            .attr('class', 'rect burnt')
            .attr('x', function(d) {return xScale(d.id) - (barWidth + 1);})
            .attr('y', function(d) {return yScale(d.hours_burnt);})
            .attr('width', barWidth)
            .attr('height', function(d) {return height - yScale(d.hours_burnt)});

        chart.selectAll('rect .planned')
            .data(data)
            .enter().append('svg:rect')
            .attr('class', 'rect planned')
            .attr('x', function(d) {return xScale(d.id) + 1})
            .attr('y', function(d) {return yScale(d.hours_planned);})
            .attr('width', barWidth)
            .attr('height', function(d) {return height - yScale(d.hours_planned)});

        chart.selectAll('text .planned')
            .data(data)
            .enter().append('text')
            .attr('class', 'label planned')
            .attr('x', function(d) {return xScale(d.id) + 4})
            .attr('y', height - 5)
            .text(function(d) {return d3.round(d.hours_planned)});

        chart.selectAll('text .burnt')
            .data(data)
            .enter().append('text')
            .attr('class', 'label planned')
            .attr('x', function(d) {return xScale(d.id) - barWidth + 3})
            .attr('y', height - 5)
            .text(function(d) {return d3.round(d.hours_burnt)});
    }

    return {
        'create': create
    };
}();

$(function() {
    // create the main chart
    ResultPerStoryChart.create();
});
