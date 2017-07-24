from errbot import BotPlugin, botcmd, arg_botcmd
from newrelic_api import Applications
from itertools import chain

import uuid

from bokeh.models import DatetimeTickFormatter
from bokeh.plotting import figure, output_file, show
from bokeh.io import export_png

import arrow
from hypfile import hipchat_file

CONFIG_TEMPLATE = {'newrelic_token': '00112233445566778899aabbccddeeff',
                   'app_ids':{
                       'us-east-1': 1234567,
                       'eu-west-1': 1234567,
                       'eu-central-1': 1234567}}


def configure(self, configuration):
    if configuration is not None and configuration != {}:
        config = dict(chain(CONFIG_TEMPLATE.items(),
                            configuration.items()))
    else:
        config = CONFIG_TEMPLATE
    super(OpsWorks, self).configure(config)

class Newrelic(BotPlugin):
    """
    This is a Newrelic Chatbot plugin to throw up graphs
    for the response times for given time period
    """
    def get_configuration_template(self):
        return CONFIG_TEMPLATE

    def create_plot(self,token,app_id,metric_name):
        hd = Applications(token).metric_data(app_id,[metric_name],['average_response_time'])
        x = []
        y = []

        for timeslice in hd['metric_data']['metrics'][0]['timeslices']:
            x.append(arrow.get(timeslice['to']).to('local').time())
            y.append(timeslice['values']['average_response_time'])

        p = figure(title="Response Time of App", plot_width=800, plot_height=400, x_axis_label='Time', y_axis_label='Avg Response Time', x_axis_type='datetime')
        p.xaxis.formatter = DatetimeTickFormatter(minutes=["%H:%M"])
        p.line(x, y, legend="Response Time.", line_width=2)
        return p
        

    @arg_botcmd('region', type=str)
    def newrelic_get_app_response_time(self, msg, region='us-east-1'):
        """
        Get response of application for a given region
        """

        token = self.config['newrelic_token']
        app_id = self.config['app_ids'][region]
        metric_name = 'HttpDispatcher'
    
        plot = self.create_plot(token, app_id, metric_name)
        image_name = "app_reponse_time_{0}.png".format(uuid.uuid4().hex)
        image_file = "/tmp/{0}".format(image_name)
      
        room = msg.frm.room
        token = self.bot_config.BOT_IDENTITY['token']
        image = export_png(plot, filename=image_file)

        filepath = image
        hipchat_file(token, room, filepath, host='api.hipchat.com')
        return "I hope this helps?"


    @arg_botcmd('region', type=str)
    def newrelic_get_db_response_time(self, msg, region='us-east-1'):
        """
        Get response of application for a given region
        """

        token = self.config['newrelic_token']
        app_id = self.config['app_ids'][region]
        metric_name = 'Datastore/MySQL/allWeb'
    
        plot = self.create_plot(token, app_id, metric_name)
        image_name = "app_reponse_time_{0}.png".format(uuid.uuid4().hex)
        image_file = "/tmp/{0}".format(image_name)
      
        room = msg.frm.room
        token = self.bot_config.BOT_IDENTITY['token']
        image = export_png(plot, filename=image_file)

        filepath = image
        hipchat_file(token, room, filepath, host='api.hipchat.com')
        return "I hope this helps?"
