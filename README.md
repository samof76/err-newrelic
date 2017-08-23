# err-newrelic

This a plugin is to get some graphs from your newrelic account. This was specifically developed for in house use, we have three newrelic application ids each representing different regions. Needs to passed using the partial configuration mechanism described [here](http://errbot.io/en/latest/user_guide/plugin_development/configuration.html).

> NOTE: This is tested on HipChat

### Installation

```
!repos install https://github.com/samof76/err-newrelic
```

This will install newrelic on plugin. See its help,

```
!help Newrelic
Newrelic
This is a Newrelic Chatbot plugin to throw up graphs
    for the response times for given time period
• !newrelic get app response time - usage: newrelic_get_app_response_time [-h] [--region REGION]
• !newrelic get db response time - usage: newrelic_get_db_response_time [-h] [--region REGION]
• !newrelic get error rate - usage: newrelic_get_error_rate [-h] [--region REGION]
• !newrelic test - (undocumented)
```

_Since this uses python [Bokeh](http://bokeh.pydata.org) package, you would need phantomjs(and hence nodejs) to export graphs as png._

```
npm install -g phantomjs-prebuilt
```

### Plugin Configuration

Since the newrelic keys and app ids are a secret, we use partial configuration mechanism to configure Newrelic keys.

```
!plugin !plugin config Newrelic {'app_ids':{'us-east-1': 111111111 , 'eu-west-1': 111111111, 'eu-central-1': 11111111}, 'newrelic_token':'1791fc61738c8521876d74'}
```

> NOTE: `us-east-1` etc., are app ids of that region.

