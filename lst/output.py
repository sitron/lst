import json
import os
import unicodedata
import re
import distutils.sysconfig

from string import Template
from datetime import datetime

from models import AppContainer


class BaseOutput(object):
    """Base class for all output classes"""

    def __init__(self, output_dir):
        self.output_dir = output_dir
        pass

    def get_output_stream(self, path):
        return open(path, 'w')

    def get_output_path(self, path):
        return self.output_dir + path

    def debug(self, data):
        data_output = open(self.output_dir + 'data.json', 'w')
        data_output.write(json.dumps(data))
        data_output.close()


class TemplatedOutput(BaseOutput):
    """Base class for output which need access to predefined html templates"""

    def __init__(self, output_dir):
        super(TemplatedOutput, self).__init__(output_dir)
        if AppContainer.dev_mode:
            self.template_dir_path = 'lst/html_templates/'
        else:
            self.template_dir_path = os.path.join(distutils.sysconfig.get_python_lib(), 'lst', 'html_templates/')
        self.abs_template_dir_path = os.path.abspath(self.template_dir_path) + '/'

    def get_template(self, name):
        graph_file = open(self.template_dir_path + name)
        graph_str = graph_file.read()
        graph_file.close()
        return graph_str


class SprintBurnUpOutput(TemplatedOutput):
    """Generates sprint burnup chart"""

    def __init__(self, output_dir):
        super(SprintBurnUpOutput, self).__init__(output_dir)

    def output(self, sprint_name, data, commited_values, sprint_data, title):
        print 'Retrieving base graph'
        try:
            template = Template(self.get_template('sprint_burnup.html'))
        except Exception as e:
            print 'Couldnt find the base graph file', e

        print 'Writing graph'
        try:
            path = 'sprint_burnup-%s-%s.html' % (
                Helper.slugify(sprint_name),
                datetime.now().strftime("%Y%m%d")
            )
            stream = self.get_output_stream(self.get_output_path(path))
            output_file_absolute = os.path.abspath(self.get_output_path(path))
            stream.write(
                template.safe_substitute(
                    template_dir_path=self.abs_template_dir_path,
                    data=json.dumps(data),
                    commited_values=json.dumps(commited_values),
                    sprint=json.dumps(sprint_data),
                    sprint_title= title
                )
            )
            stream.close()
            print 'Check your new graph at ' + output_file_absolute
        except Exception as e:
            print 'Problem with the generation of the graph file', e


import pygal
from pygal.style import LightColorizedStyle
import io
from bs4 import BeautifulSoup


class OutputHelper(object):
    @classmethod
    def get_base_html_structure(cls):
        html_str = u"""
        <html>
            <head>
                <title>LST graph</title>
                <script type="text/javascript" src="http://kozea.github.com/pygal.js/javascripts/svg.jquery.js"></script>
                <script type="text/javascript" src="http://kozea.github.com/pygal.js/javascripts/pygal-tooltips.js"></script>
            </head>
            <body>
                <h1>{}</h1>
                <div class="content">
                    <div class="main-graph">
                        <figure>
                            {}
                        </figure>
                    </div>
                </div>
            </body>
        </html>
        """
        return html_str

    @classmethod
    def output(cls, path, content):
        output_file_absolute = os.path.abspath(AppContainer.secret.get_output_dir() + path)
        with io.open(output_file_absolute, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_file_absolute


class SprintBurnUpChart(object):
    @classmethod
    def get_chart(cls, dates, series):
        biggest_y_value = 100
        for values in series.values():
            biggest_y_value = max(biggest_y_value, values[-1])

        chart = pygal.Line(x_label_rotation=20,
                           include_x_axis=True,
                           range=(0, biggest_y_value),
                           style=LightColorizedStyle,
                           explicit_size=True,
                           height=700,
                           print_values=False,
                           no_prefix=True,
                           background=False,
                           disable_xml_declaration=True)

        chart.x_labels = map(str, dates)
        for key,entries in series.items():
            chart.add(key, entries)

        return chart

    @classmethod
    def get_sprint_burnup_html_structure(cls, series):
        html = BeautifulSoup(OutputHelper.get_base_html_structure())

        # top graph container
        content = html.find(class_="content")
        top_graphs_container = html.new_tag('div')
        top_graphs_container['class'] = 'top-graphs'
        content.insert(0, top_graphs_container)

        # top graphs
        for serie in series:
            figure = html.new_tag('figure')
            figure.string = '{}'
            figure['class'] = serie
            caption = html.new_tag('figcaption')
            caption.string = '{}'
            figure.insert(0, caption)
            top_graphs_container.append(figure)

        # velocity container
        velocity = html.new_tag('p')
        velocity['class'] = 'velocity'
        velocity.string = '{}'
        content.insert(0, velocity)

        # custom css
        css_url = 'http://sitron.github.io/lst/stylesheets/charts.css'
        if AppContainer.dev_mode:
            css_url = os.path.abspath('lst/css/charts.css')
        custom_css = html.new_tag('link', href=css_url, rel='stylesheet')
        html.head.insert(2, custom_css)

        return html.prettify()


class ResultPerValuePie(object):
    @classmethod
    def get_chart(cls, result):
        """
        Get a pie chart for sprint results

        :param result: tuple (actual, commited)
        :param graph_title: title
        """
        percent = (result[0] / result[1]) * 100

        chart = pygal.Pie(x_label_rotation=20,
                          show_legend=False,
                          background=False,
                          explicit_size=True,
                          width=200,
                          height=200,
                          no_prefix=True,
                          margin=0,
                          include_x_axis=False,
                          style=LightColorizedStyle,
                          print_values=False,
                          disable_xml_declaration=True)
        chart.add('Result', percent)
        chart.add('Remaining ', 100-percent if percent <= 100 else 0)

        return chart


class ResultPerStoryChart(object):
    @classmethod
    def get_chart(cls, story_ids, series):

        chart = pygal.Bar(x_label_rotation=20,
                          include_x_axis=True,
                          style=LightColorizedStyle,
                          explicit_size=True,
                          height=700,
                          print_values=False,
                          no_prefix=True,
                          background=False,
                          disable_xml_declaration=True)

        chart.x_labels = map(str, story_ids)
        for key, entries in series.items():
            chart.add(key, entries)

        return chart


class ResultPerStoryOutput(TemplatedOutput):
    """Generates bar graph for each sprint story's result"""

    def __init__(self, output_dir):
        super(ResultPerStoryOutput, self).__init__(output_dir)

    def output(self, sprint_name, data):
        print 'Retrieving base graph'
        try:
            template = Template(self.get_template('result_per_story.html'))
        except Exception as e:
            print 'Couldnt find the base html file to print result per story', e

        print 'Writing graph'
        try:
            path = 'result_per_story-%s-%s.html' % (
                Helper.slugify(sprint_name),
                datetime.now().strftime("%Y%m%d")
            )
            stream = self.get_output_stream(self.get_output_path(path))
            output_file_absolute = os.path.abspath(self.get_output_path(path))
            stream.write(
                template.safe_substitute(
                    template_dir_path=self.abs_template_dir_path,
                    data=json.dumps(data),
                )
            )
            stream.close()
            print 'Check your new graph at ' + output_file_absolute
        except Exception as e:
            print 'Problem with the generation of the graph file', e


class Helper(object):
    @staticmethod
    def slugify(s):
        slug = unicodedata.normalize('NFKD', s)
        slug = slug.encode('ascii', 'ignore').lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
        slug = re.sub(r'[-]+', '-', slug)
        return slug
