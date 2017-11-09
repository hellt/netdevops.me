---
date: 2017-11-09T12:00:00Z
keywords:
- Flask
- nginx
- uWSGI
- Docker
tags:
- Flask
- nginx
- uWSGI
- Docker

title: Flask application in a production-ready container

---

Flask documentation [is very clear](http://flask.pocoo.org/docs/0.12/deploying/#deployment-options) on where is the place for its built-in WSGI application server:

> While lightweight and easy to use, **Flask’s built-in server is not suitable for production** as it doesn’t scale well and by default serves only one request at a time. 

So how about I share with you a [_Dockerfile_](https://github.com/hellt/nginx-uwsgi-flask-alpine-docker) that will enable your Flask application to run **properly** and ready for production-like deployments? As a bonus, I will share my findings discovered along the way of building this container image.

![nginx-uwsgi-flaks-alpine-docker](https://gitlab.com/rdodin/netdevops.me/uploads/e893ab9ea824ed501170908377d3fb52/image.png)

<!--more-->

But before we dive in and start throwing words like uwsgi, nginx and sockets lets set up our vocabulary. As DigitalOcean originally wrote:

> * [**WSGI**](https://www.python.org/dev/peps/pep-3333/): A Python spec that defines a standard interface for communication between an application or framework and an application/web server. This was created in order to simplify and standardize communication between these components for consistency and interchangeability. This basically defines an API interface that can be used over other protocols.
> * [**uWSGI**](https://uwsgi-docs.readthedocs.io/en/latest/): An application server container that aims to provide a full stack for developing and deploying web applications and services. The main component is an application server that can handle apps of different languages. It communicates with the application using the methods defined by the WSGI spec, and with other web servers over a variety of other protocols. This is the piece that translates requests from a conventional web server into a format that the application can process.
> * [**uwsgi**](https://uwsgi-docs.readthedocs.io/en/latest/Protocol.html): A fast, binary protocol implemented by the uWSGI server to communicate with a more full-featured web server. This is a wire protocol, not a transport protocol. It is the preferred way to speak to web servers that are proxying requests to uWSGI.

## Why do we even need nginx and uWSGI in front of Flask?
That is the question everyone should ask. Main reason is performance, of course. The Flasks built-in web server is a development server by [Werkzeug](http://werkzeug.pocoo.org/docs/0.12/) which was not designed to be particularly efficient, stable, or secure.  
And by all means Werkzeug was not optimized to serve static content, that is why production deployments of Flask apps rely on the following stack:

1. **Front-end web-server** (nginx or Apache): load balancing, SSL termination, rate limiting, HTTP parsing and serving static content.
2. **WSGI application server** (uWSGI, Gunicorn, CherryPy): runs WSGI compliant web applications and does it in a production-grade manner. Handling concurrent requests, process management, cluster membership, logging, configuration, shared memory, etc.

Obviously, development server which comes with Flask simply does not bother about all these tasks that production deployments face. That is why it is so strongly advised against using Flask' server in any kind of production.

> Speaking about the performance I suggest to check out this presentation from Pycon IE '13 called [_Maximum Throughput (baseline costs of web frameworks)_](http://brianmcdonnell.github.io/pycon_ie_2013/#/) that explains how number of queries per second depends on web stack you choose.

While there are many alternatives to [`nginx`](https://nginx.ru/en/)+[`uWSGI`](https://uwsgi-docs.readthedocs.io/en/latest/) pair, I will focus on these two in this post.

## Do I need a _production grade_ Flask app for a pet project?
While you may go with built-in Flask server for the little projects of your own, this container is so simple that you would not need to use the Built-in server anymore. Why opting out for testing server, if it is easy to launch it in a production-ready way?

## Configuring nginx
We start with configuration of `nginx` server that will face incoming traffic and handle it for us.

> We also keep in mind that our nginx server will run in an Alpine Linux docker container.

nginx config consists of two parts:

- global nginx config file ([`nginx.conf`](https://github.com/hellt/nginx-uwsgi-flask-alpine-docker/blob/master/python2/nginx.conf))
- site-specific config file ([`flask-site-nginx.conf`](https://github.com/hellt/nginx-uwsgi-flask-alpine-docker/blob/master/python2/flask-site-nginx.conf))

### nginx global config
For the **global nginx config file** I combined the recommendations outlined in the post [_How to Configure NGINX for a Flask Web Application_](http://www.patricksoftwareblog.com/how-to-configure-nginx-for-a-flask-web-application/) with [nginx configuration samples](https://uwsgi-docs.readthedocs.io/en/latest/Nginx.html) from uWSGI docs.

A little caveat that you might encounter when deploying nginx in Alpine Linux renders itself like that:
```
Error: nginx: [emerg] open() "/run/nginx/nginx.pid" failed (2: No such file or directory)
```

All you need to do is to to [change pid file location](https://github.com/hellt/nginx-uwsgi-flask-alpine-docker/blob/master/python2/nginx.conf#L10) since `/run/` path is not available in Alpine Linux.

### nginx site config
Site config ([`flask-site-nginx.conf`](https://github.com/hellt/nginx-uwsgi-flask-alpine-docker/blob/master/python2/flask-site-nginx.conf)) is short and simple:
```
server {
    location / {
        try_files $uri @yourapplication;
    }
    location @yourapplication {
        include uwsgi_params;
        uwsgi_pass unix:///tmp/uwsgi.sock;
    }
    # Configure NGINX to deliver static content from the specified folder
    location /static {
        alias /app/static;
    }
}
```
Basically, all you saying here is that your application will be served at `/` endpoint and use `uwsgi` wire protocol via unix socket at `unix:///tmp/uwsgi.sock`.

Also we ask nginx to serve static content that is stored in `/app/static`.

Communication path between nginx and WSGI app server can be configured with different sockets and protocols, but `unix_socket + uwsgi protocol` tends to be the most appropriate way.

> ![sockets_perf](https://gitlab.com/rdodin/netdevops.me/uploads/a618d2c1e3d19c9a8dbf9d2d23f2cbd9/image.png)
> The uwsgi protocol is derived from SCGI but with binary string length representations and a 4-byte header that includes the size of the var block (16 bit length) and a couple of general-purpose bytes. Binary management is much easier and cheaper than string parsing.

So far we dealt with the first bastion, which is nginx config. Our configuration path can be depicted as that:

> ![nginx_configured](https://gitlab.com/rdodin/netdevops.me/uploads/b6102940c48b80bcb7578cf9c53daf0e/image.png)

## uWSGI configuration
uWSGI [documentation](https://uwsgi-docs.readthedocs.io/) is extensive, you may find all the tweaks and recommendations for the wide range of deployment scenarios. Since this container we build is of general purpose, a sensible uWSGI configuration file ([`uwsgi.ini`](https://github.com/hellt/nginx-uwsgi-flask-alpine-docker/blob/master/python2/uwsgi.ini)) could look as follows:
```
[uwsgi]
module = main
callable = app
plugins = /usr/lib/uwsgi/python

uid = nginx
gid = nginx

socket = /tmp/uwsgi.sock
chown-socket = nginx:nginx
chmod-socket = 664

cheaper = 1
processes = %(%k + 1)
```

This configuration file consists of uWSGI options each of which is [documented](https://uwsgi-docs.readthedocs.io/en/latest/Options.html) quite extensively.

### Module and Callable
We start with defining where is an entry point for uWSGI server to call our app.  
The [`module`](https://uwsgi-docs.readthedocs.io/en/latest/Options.html#module) directive corresponds to the name of the python module holding your app. In my case the demo Flask app I built is contained in the [`main.py`](https://github.com/hellt/nginx-uwsgi-flask-alpine-docker/blob/master/python2/app/main.py) file, hence the `main` module name.  
On the other hand, [`callable`](https://uwsgi-docs.readthedocs.io/en/latest/Options.html#callable) is the name of an object inside your module, which is a Flask application entry point.
```python
# coding: utf-8
from flask import Flask

app = Flask(__name__)
# rest output is omitted
```
For me, its the `app` variable that should be populated to the `callable` parameter.

### Plugins
uWSGI is modular and language-agnostic. In Apline Linux deployments it comes with core features built in, but python support is not one of them.

> uWSGI can include features in the core or as loadable plugins. uWSGI packages supplied with OS distributions tend to be modular. In such setups, be sure to load the plugins you require with the plugins option.

That is why [`plugins`](https://uwsgi-docs.readthedocs.io/en/latest/Options.html#plugins) parameter is needed where we specify where to find the python plugin. I installed `uwsgi-python` via apt package manager, this step will be covered as we move to Dockerfile explanation section.

### uid, gid
Common sense: do not run uWSGI instances as root. You can start your uWSGIs as root, but be sure to drop privileges with the uid and gid options.

I dropped privileges to `nginx` user level.

### Socket configuration
As you remember, we agreed that uwsgi protocol over unix socket will be used as a communication suite between nginx and uWSGI. We already told so to nginx, now its time for uWSGI.

Same `/tmp/uwsgi.sock` is referenced in this `uwsgi.ini` file. Moreover, we change permissions to that socket file to be readable for `nginx` user.

## Processes configuration
uWSGI can spawn multiple processes to run your Flask app, being very productive. But, you need to thoroughly calculate how many processes and threads works for your particular situation.

> There is no magic rule for setting the number of processes or threads to use. It is very much application and system dependent. Simple math like `processes = 2 * cpucores` will not be enough. You need to experiment with various setups and be prepared to constantly monitor your apps. `uwsgitop` could be a great tool to find the best values.

In our config file these two lines will do the trick:
```
cheaper = 1
processes = %(%k + 1)
```
With `cheaper = 1` we activate the [The uWSGI cheaper subsystem](http://uwsgi-docs.readthedocs.io/en/latest/Cheaper.html) which allows to dynamically scale the number of running workers (processes). So under the minimum load uWSGI will spawn just one workers.

The upper limit is dictated by `processes = %(%k + 1)` statement. The `%k` is a [magic variable](https://uwsgi-docs.readthedocs.io/en/latest/Configuration.html#magic-variables), which will be resolved by uWSGI to the number of available cores. So for a single core system, number of max workers will be `1 + 1 = 2`.

We finished another configuration block:

> ![nginx_uwsgi_configured](https://gitlab.com/rdodin/netdevops.me/uploads/3a0a46936db55c52f4f5750cf4e9ab36/image.png)

## Supervisord to rule them all
A cherry on a pie is to use the `supervisord` service to manage nginx and uWSGI. For that we create [`supervisord.conf`](https://github.com/hellt/nginx-uwsgi-flask-alpine-docker/blob/master/python2/supervisord.conf) with a plain and simple config.

Supervisord will watch for these process and restart/start them automatically if things go south for one of them.

## Lets load it in a container?
Our final part will be creating a lightweight Alpine Linux Docker container image that will have all these parts inside ready to consume.

Refer to this comments-rich [Dockerfile](https://github.com/hellt/nginx-uwsgi-flask-alpine-docker/blob/master/python2/Dockerfile) where we glue together all the things we discussed above in a docker image.

One thing to mention here is that python2 and python3 uWSGI plugins are separate packages in Alpine packages system.

## Enjoying the result
I built [two container images](https://hub.docker.com/r/hellt/nginx-uwsgi-flask-alpine-docker/) for python2 and python3 respectively along with a sample python application. Lets taste them out:

```bash
# pull the image (tagged py2 or py3 respectively)
[ec2~]$ sudo docker pull hellt/nginx-uwsgi-flask-alpine-docker:py3
py3: Pulling from hellt/nginx-uwsgi-flask-alpine-docker
b56ae66c2937: Already exists
# omitted
Status: Downloaded newer image for hellt/nginx-uwsgi-flask-alpine-docker:py3
```
The image is very lightweight (62 MB):
```
REPOSITORY                              TAG                 IMAGE ID            CREATED             SIZE
hellt/nginx-uwsgi-flask-alpine-docker   py3                 7fb6af3baf0e        6 minutes ago       62.5 MB
```

Since docker image contains a sample application we can run it to test that everything works as expected:
```bash
sudo docker run -p 38080:80 hellt/nginx-uwsgi-flask-alpine-docker:py3
```

> ![final_result](https://gitlab.com/rdodin/netdevops.me/uploads/36bf92416a511abfd642d15de44e9387/image.png)
> Voila

## How do I use this one?
First of all, there is no need to use the image from the docker hub, it was created for demonstration purposes. To create the same container but for your application, consider the following steps:

1. Clone the [repo](https://github.com/hellt/nginx-uwsgi-flask-alpine-docker) with the Dockerfile and configuration files
2. Tune the config files if necessary:
    1. Tune `uwsgi.ini` config: i.e. `cheaper` number and `processes` to match your hardware
    2. Enhance nginx config
3. Copy your app to the `/app` subdirectory and you are good to build your image

> Post comments [are here](https://gitlab.com/rdodin/netdevops.me/issues/5history).