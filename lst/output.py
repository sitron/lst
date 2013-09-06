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
