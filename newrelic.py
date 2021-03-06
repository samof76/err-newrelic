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
    super(Newrelic, self).configure(config)

class Newrelic(BotPlugin):
    """
    This is a Newrelic Chatbot plugin to throw up graphs
    for the response times for given time period
    """
    def get_configuration_template(self):
        return CONFIG_TEMPLATE

    @arg_botcmd('--region', dest='region', type=str, help='region where the app is running!', default='us-east-1')
    def newrelic_get_app_response_time(self, msg, region):
        """
        Get response of application for a given region
        """

        token = self.config['newrelic_token']
        app_id = self.config['app_ids'][region]
        metric_name = 'HttpDispatcher'

        hd = Applications(token).metric_data(app_id,['HttpDispatcher'],['average_response_time'])
        x = []
        y = []

        for timeslice in hd['metric_data']['metrics'][0]['timeslices']:
            x.append(arrow.get(timeslice['to']).to('Asia/Kolkata').time())
            y.append(timeslice['values']['average_response_time'])

        plot = figure(title="Response Time of App",
                        plot_width=800, plot_height=400,
                        x_axis_label='Time',
                        y_axis_label='Avg Response Time(ms)',
                        x_axis_type='datetime')
        plot.xaxis.formatter = DatetimeTickFormatter(minutes=["%H:%M"])
        plot.line(x, y, legend="Response Time.", line_width=2)
    
        image_name = "app_reponse_time_{0}.png".format(uuid.uuid4().hex)
        image_file = "/tmp/{0}".format(image_name)
      
        room = msg.frm.room
        token = self.bot_config.BOT_IDENTITY['token']
        image = export_png(plot, filename=image_file)

        filepath = image
        hipchat_file(token, room, filepath, host='api.hipchat.com')
        return "I hope this helps?"


    @arg_botcmd('--region', dest='region', type=str, help='region where the db is running!', default='us-east-1')
    def newrelic_get_db_response_time(self, msg, region):
        """
        Get response of application for a given region
        """

        token = self.config['newrelic_token']
        app_id = self.config['app_ids'][region]
        metric_name = 'Datastore/MySQL/allWeb'

        data = Applications(token).metric_data(app_id,
                                            ['HttpDispatcher','Datastore/MySQL/allWeb'],
                                            ['average_response_time','call_count'])
        
        for metric in data['metric_data']['metrics']:
            if metric['name'] == 'HttpDispatcher':
                hd_timeslices = metric['timeslices']
            if metric['name'] == 'Datastore/MySQL/allWeb':
                ds_timeslices = metric['timeslices']

        x = []
        y = []
        hd_timeslices.reverse()
        for ds_timeslice in ds_timeslices:
            x.append(arrow.get(ds_timeslice['to']).to('Asia/Kolkata').time())
            hd_timeslice = hd_timeslices.pop()
            datastore_time = (ds_timeslice['values']['average_response_time']*ds_timeslice['values']['call_count'])/float(hd_timeslice['values']['call_count'])  
            y.append(datastore_time)

        plot = figure(title="Response Time of DB",
                    plot_width=800,
                    plot_height=400,
                    x_axis_label='Time',
                    y_axis_label='Avg Response Time(ms)',
                    x_axis_type='datetime')

        plot.xaxis.formatter = DatetimeTickFormatter(minutes=["%H:%M"])
        plot.line(x, y, legend="Response Time.", line_width=2)
  
        image_name = "db_reponse_time_{0}.png".format(uuid.uuid4().hex)
        image_file = "/tmp/{0}".format(image_name)
      
        room = msg.frm.room
        token = self.bot_config.BOT_IDENTITY['token']
        image = export_png(plot, filename=image_file)

        filepath = image
        hipchat_file(token, room, filepath, host='api.hipchat.com')
        return "I hope this helps?"

    @arg_botcmd('--region', dest='region', type=str, help='region where the db is running!', default='us-east-1')
    def newrelic_get_error_rate(self, msg, region):
        """
        Get response of application for a given region
        """

        token = self.config['newrelic_token']
        app_id = self.config['app_ids'][region]
        metric_name = 'Errors/all'
    
        data = Applications(token).metric_data(app_id,['HttpDispatcher','Errors/all','OtherTransaction/all'],['error_count','call_count'])

        ot_timeslices = []
        for metric in data['metric_data']['metrics']:
            if metric['name'] == 'HttpDispatcher':
                hd_timeslices = metric['timeslices']
            if metric['name'] == 'Errors/all':
                ea_timeslices = metric['timeslices']
            if metric['name'] == 'OtherTransaction/all':
                ot_timeslices = metric['timeslices']

        x = []
        y = []
        hd_timeslices.reverse()
        ot_timeslices.reverse()

        for ea_timeslice in ea_timeslices:
            x.append(arrow.get(ea_timeslice['to']).to('Asia/Kolkata').time())
            hd_timeslice = hd_timeslices.pop()
            if len(ot_timeslices):
                ot_timeslice = ot_timeslices.pop()
            else:
                ot_timeslice = {'values': {'call_count': 0}}

            error_rate = 100 * ea_timeslice['values']['error_count']/float(hd_timeslice['values']['call_count']+ot_timeslice['values']['call_count'])  
            y.append(error_rate)


        plot = figure(title="App Error Rate(%)",
                    plot_width=800,
                    plot_height=400,
                    x_axis_label='Time',
                    y_axis_label='Error Rate(%)',
                    x_axis_type='datetime')

        plot.xaxis.formatter = DatetimeTickFormatter(minutes=["%H:%M"])
        plot.line(x, y, legend="Response Time.", line_width=2)

        image_name = "app_error_rate_{0}.png".format(uuid.uuid4().hex)
        image_file = "/tmp/{0}".format(image_name)
      
        room = msg.frm.room
        token = self.bot_config.BOT_IDENTITY['token']
        image = export_png(plot, filename=image_file)

        filepath = image
        hipchat_file(token, room, filepath, host='api.hipchat.com')
        return "I hope this helps?"
