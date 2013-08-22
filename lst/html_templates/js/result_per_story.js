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
        var
            height = 400,
            width = 800,
            barWidth = 30,
            barSpace = 2,
            xScale,
            yScale,
            chart,
            xAxis,
            yAxis,
            axisContainer,
            storyIds = data.map(function(d) {return d.id;}),
            storyBurnt = data.map(function(d) {return d.hours_burnt;}),
            storyPlanned = data.map(function(d) {return d.hours_planned;}),
            maxBurnt = d3.max(storyBurnt),
            maxPlanned = d3.max(storyPlanned),
            max = Math.max(maxBurnt, maxPlanned);

        // scales
        xScale = d3.scale.ordinal()
            .domain(storyIds)
            .rangePoints([0, width], 1)

        yScale = d3.scale.linear()
            .domain([0, max])
            .range([height, '0'])

        // chart container
        chart = d3.select('#graph').append('svg')
            .attr('class', 'chart')
            .attr('width', width + 100)
            .attr('height', height + 100)
            .append('g')
            .attr('transform', 'translate(40, 20)');

        // axis
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

        // series
        var properties = [
            {name: 'hours_burnt', position: -(barWidth + barSpace)},
            {name: 'hours_planned', position: barSpace}
        ];

        properties.forEach(function(item) {
            container = chart.selectAll('.bar-container.' + item.name)
                .data(data)
                .enter().append('svg:g')
                .attr('class', 'bar-container ' + item.name)
                .attr('transform', function(d) {return 'translate(' + (xScale(d.id) + item.position) + ', ' + height + ')'});

            container
                .append('svg:rect')
                .attr('class', 'rect ' + item.name)
                .attr('width', barWidth)
                .attr('height', function(d) {return height - yScale(d[item.name]);})
                .attr('y', function(d) {return - (height - yScale(d[item.name]));});

            container
                .append('text')
                .attr('class', 'label ' + item.name)
                .attr('x', barWidth / 2)
                .attr('y', -10)
                .attr('text-anchor', 'middle')
                .text(function(d) {return d3.round(d[item.name])});
        });
    }

    return {
        'create': create
    };
}();

$(function() {
    // create the main chart
    ResultPerStoryChart.create();
});
