---
date: 2019-06-30T06:00:00Z
comment_id: gcp-function
keywords:
- GCP
- GCP Function
- Python
- Serverless
tags:
- GCP
- GCP Function
- Python
- Serverless

title: Creating Google Cloud Platform Function with Python and Serverless
---
![serveless](https://gitlab.com/rdodin/pics/-/wikis/uploads/e4f956d64dcf812f64a77f8532499d07/image.png)
Two years ago [I shared](../../2017/building-aws-lambda-with-python-s3-and-serverless/) my experience on building the AWS Lambda function for a python project of my own. And a few days ago I stumbled upon a nice opensource CLI tool that I immediately wanted to transform in a web service.

Naturally, a simple, single-purpose tool is a perfect candidate for function-as-a-service (FaaS), and since I had past experience with AWS Lambda, this time I decided to meet its Google's sibling - [Google Cloud Function](https://cloud.google.com/functions/).

In this post we'll discover how to take a python package with 3rd party dependencies, make a GCP Function from it and deploy it without a single click in the UI - all without leaving the IDE.

[[Project's source code](https://github.com/hellt/pycatj-web)]
<!--more-->

The python tool I considered a natural fit for a Cloud Function is a [`pycatj`](https://github.com/dbarrosop/pycatj) by **David Barroso** that he released just recently.

<center>{{< tweet 1143810284513107968>}}</center>

This tool helps you to map a JSON/YAML file to a Python dictionary highlighting the keys you need to access the nested data:

```json
$ cat tests/data/test_1.json
{
    "somekey": "somevalue",
    "somenumber": 123,
    "a_dict": {
        "asd": "123",
        "qwe": [1, 2, 3],
        "nested_dict": {
            "das": 31,
            "qwe": "asd"
        }
    }
}

$ pycatj --root my_var tests/data/test_1.json
my_var["somekey"] = "somevalue"
my_var["somenumber"] = 123
my_var["a_dict"]["asd"] = "123"
my_var["a_dict"]["qwe"][0] = 1
my_var["a_dict"]["qwe"][1] = 2
my_var["a_dict"]["qwe"][2] = 3
my_var["a_dict"]["nested_dict"]["das"] = 31
my_var["a_dict"]["nested_dict"]["qwe"] = "asd"
```

I felt like having a single-page web service that would do these transformations leveraging the `pycatj` would be helpful to somebody sometime.  
Probably the easiest way would be to rewrite the same code with JavaScript and create a static page with that code without any backend, but _does it spark joy?_. Not even a bit.

And as a starting point I decided to create a serverless function that will rely on `pycatj` and will be triggered later by a Web frontend with an HTTP request carrying the content for _pycatj-ifying_.

In a nutshell, the function should behave something like that:

```bash
curl -X POST https://api-endpoint.com -d '{"data":{"somekey":"value1"}}'
# returns
my_var["somekey"] = "value1"
```

To add some sugar to the mix I will leverage the [serverless](https://serverless.com) framework to do the heavy lifting in a code-first way. The plan is set, lets go see it to completion.

# Agenda
The decomposition of the service creation and deployment can be done as follows:

1. Google Cloud Platform
   1. Create a GCP account (if needed) and acquire the API credentials
   2. Create a project in GCP that will host a Function and enable the needed APIs for serverless to be able to create the Function and its artifacts
2. Function creation and testing
   1. create the code in conformance with the GCP Function handlers/events rules
   2. Manage code dependencies
3. Function deployment
   1. leveraging serverless framework to deploy a function to GCP
4. Add a frontend (in another blog post) that will use the serverless function.

# 1 Google Cloud Platform
Following the agenda, ensure that you have a working GCP account (trial gives you $300, and GCP Function is perpetually FREE with the sane usage thresholds). Make sure that you have a billing account created, this is set up when you opt in the free trial program, for example. Without a linked billing account the Functions won't work.

Once you have your account set, you should either continue with a default project or create a new one. In either case you need to enable the APIs that will be leveraged by serverless framework for a function deployment process. Go thru [this guide](https://serverless.com/framework/docs/providers/google/guide/credentials/) carefully on how to enable the right APIs.

**API credentials**

Do not forget to download your API credentials, as nothing can be done without them. This [guide's section](https://serverless.com/framework/docs/providers/google/guide/credentials/#get-credentials--assign-roles) explains it all.  
The commands you will see in the rest of this post assume that the credentials are stored in `~/.gcould` directory.

# 2 Function creation
Since we are living on the edge, we will rely on the [serverless](https://serverless.com) framework to create & deploy our function. The very same framework [I leveraged](2017/building-aws-lambda-with-python-s3-and-serverless/) for the AWS Lambda creation, so why not try it for GCP Function?

The notable benefit of serverless framework is that it allows you to define your Function deployment _as a code_ and thus making it repeatable, versionable and fast.

But nothing comes cheap, for all these perks you need to pay; and the serverless toll is in being a Javascript package =|. Don't know about you, but _no glove - no love_ is the principle I try to stick to with JS. So why not quarantine it in a [docker container](https://hub.docker.com/r/amaysim/serverless) jail and keep your machine npm-free?

```bash
docker pull amaysim/serverless:1.45.1
```
## 2.1 Serverless service template
The way I start my serverless journey is by telling the serverless to [generate a service template](https://serverless.com/framework/docs/providers/google/cli-reference/create/#available-templates) in the programming language of my choice. Later we can tune bits and pieces of that [service](https://serverless.com/framework/docs/providers/aws/guide/services/), but if you start from a zero-ground, its easier to have a scaffolding to work on.

```bash
# Create service with `google-python` template in the folder ~/projects/pycatj-web
docker run --rm \
 -v ~/projects/pycatj-web:/opt/app \
 amaysim/serverless:1.45.1 \
 serverless create --template google-python --path pycatj-serverless
```

The result of the `serverless create --template <template>` command will be a directory with a boilerplate code for our function and a few serverless artifacts.
```bash
# artifacts created by `serverless create --template`
$ tree pycatj-serverless/
pycatj-serverless/
├── main.py
├── package.json
└── serverless.yml
```
We need to take a closer look at the generated `serverless.yml` template file where we need to make some adjustments:

1. the project name should match the project name you have created in the GCP
2. the path to your GCP credentials json file should be valid

Given that the project in my GCP is called `pycatj` and my credentials file is `~/.gcloud/pycatj-d6af60eda976.json` the `provider` section of the `serverless.yml` file would look like this:

```yml
# serverless.yml file
# with project name and credentials file specified
provider:
  name: google
  stage: dev
  runtime: python37
  region: us-central1
  project: pycatj
  credentials: ~/.gcloud/pycatj-d6af60eda976.json
```

As to the `main.py` generated by the framework, then its a simple boilerplate code with a text reply to an incoming HTTP request wrapped in a Flask object. 
```python
# main.py
def http(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    return f'Hello World!'
```

Lets test that our modifications work out so far by trying to deploy the template service.

## 2.2 Testing function deployment
Before we start pushing our function and its artifacts to the GCP, we need to tell serverless how to talk to the cloud provider. To do that, we need to install the `serverless-google-cloudfunctions` plugin that is [referenced](https://github.com/hellt/pycatj-web/blob/master/pycatj-serverless/serverless.yml#L18) in the `serverless.yml` file.

Install the google cloud functions plugin with the `npm install` command using the directory with a generated serverless service files:

```bash
docker run --rm \
  -v ~/.gcloud/:/root/.gcloud \
  -v ~/projects/pycatj-web/pycatj-serverless:/opt/app \
  amaysim/serverless:1.45.1 npm install
```
Note, here I mount my GCP credentials that are stored at `~/.gcloud` dir to a containers `/root/.gcloud` dir where serverless container will find them as they are referenced in the `serverless.yml` file.  
And secondly I bind mount my project's directory `~/projects/pycatj-web/pycatj-serverless` to the `/opt/app` dir inside the container that is a `WORKDIR` of that container.

Now we have a green flag to try out the deployment process with `serverless deploy`:

```
docker run --rm \
  -v ~/.gcloud/:/root/.gcloud \
  -v ~/projects/pycatj-web/pycatj-serverless:/opt/app \
  amaysim/serverless:1.45.1 serverless deploy
```

> If the deployment [fails](https://github.com/serverless/serverless-google-cloudfunctions/issues/82#issuecomment-326222674) with the **Error Not Found** make sure that you don't have stale failed deployments by going to **Cloud Console -> Deployment Manager** and deleting all deployments created by Serverless

Upon a successful deployment you will have a Cloud Function deployed and reachable by the service URL:
```
Deployed functions
first
  https://us-central1-pycatj.cloudfunctions.net/http
```

`curl`-ing that API endpoint will return a simple "Hello world" as coded in our boilerplate `main.py` function:
```python
# main.py
def http(request):
    return f'Hello World!'
```

```bash
curl -s https://us-central1-pycatj.cloudfunctions.net/http
Hello World!
```

You can also verify the resources that were created by this deployment by visiting the **Deployment Manager** in the GCP console as well as navigating to the functions page and examine the deployed function and its properties:

![function](https://gitlab.com/rdodin/pics/-/wikis/uploads/10b4d747ddda7e773d8b21767619b9df/image.png)

## 2.3 Writing a Function
That was a template [function](https://serverless.com/framework/docs/providers/google/guide/functions/) that we just [deployed](https://serverless.com/framework/docs/providers/google/guide/deploying/) with the HTTP [event](https://serverless.com/framework/docs/providers/google/guide/events/) acting as a trigger.

Lets see how the the actual Python function is coupled to a service definition inside the serverless file. How about we give our function a different name by first changing the `functions` section of the `serverless.yml` file:

```yaml
# changing the function name and handler to `pycatjify`
functions:
  pycatjify:
    handler: pycatjify
    events:
      - http: path
```

Since we changed the function and the handler name to `pycatjify` we should do the same to our function inside the `main.py` file:
```python
def pycatjify(request):
    return f"We are going to give pycatj its own place on the web!"
```

Deploying this function will give us a new API endpoint aligned to a new function name we specified in the `serverless.yml`:
```bash
Deployed functions
pycatjify
  https://us-central1-pycatj.cloudfunctions.net/pycatjify

# testing
$ curl https://us-central1-pycatj.cloudfunctions.net/pycatjify
We are going to give pycatj its own place on the web!
```
### 2.3.1 Managing code dependencies
Up until now we played with a boilerplate code with a few names changed to give our function a bit of an identity. We reached the stage when its time to onboard the `pycatj` package and make our function benefit from it.

Since the Functions are executed in the sandboxes on the cloud platforms, we must somehow tell what dependencies we want these sandbox to have when running our code. In the [AWS Lambda example](https://netdevops.me/2017/building-aws-lambda-with-python-s3-and-serverless#adding-python-packages-to-lambda) we packaged the 3rd party libraries along the function (aka vendoring).

In GCP case the [vendoring](../../2017/building-aws-lambda-with-python-s3-and-serverless/#adding-python-packages-to-lambda) approach is also possible and is done in the same way, but it is also possible to ship a pip `requirements.txt` file along your `main.py` that will specify your function dependencies as pythonistas used to.

> Read more on GCP python [dependency](https://cloud.google.com/functions/docs/writing/specifying-dependencies-python) management

Unfortunately, the PIP version that GCP currently uses does not support [PEP 517](https://www.python.org/dev/peps/pep-0517/), so it was not possible to specify `-e git+https://github.com/dbarrosop/pycatj.git#egg=pycatj` in a requirements file, thus I continued with a good old vendoring technique:

```bash
# executed in ~/projects/pycatj-web/pycatj-serverless
pip3 install -t ./vendored git+https://github.com/dbarrosop/pycatj.git
```

This installs `pycatj` package and its dependencies in a `vendored` directory and will be considered as Function's artifact and pushed to GCP along the `main.py` with the next `serverless deploy` command.

### 2.3.2 Events
Every function should be triggered by an [event or a trigger](https://cloud.google.com/functions/docs/concepts/events-triggers) that is supported by a cloud provider. When serverless is used the event type is specified for each function in the `serverless.yml` file:
```yaml
# pycatjify function is triggered by an event of type `http`
# note that they key `path` is irrelevant to the serverless
functions:
  pycatjify:
    handler: pycatjify
    events:
      - http: path
```
With this configuration we expect our function to execute once an HTTP request hits the function API endpoint.

### 2.3.3 Writing a function
Yes, a thousand words later we finally at a milestone where we write actual python code for a function. The template we generated earlier gives us a good starting point - a function body with a single [Flask `request`](http://flask.pocoo.org/docs/1.0/api/#flask.Request) argument:
```python
def pycatj(request):
    return f"We are going to give pycatj its own place on the web!"
```
The logic of our serverless function that we are coding here is:

1. parse the contents of an incoming HTTP request extracting the contents of a JSON file passed along with it
2. transform the received data with `pycatj` package and send back the response

With a few additions to access the `pycatj` package in a `vendored` directory and being able to test the function locally, the resulting [`main.py`](https://github.com/hellt/pycatj-web/blob/master/pycatj-serverless/main.py) file looks as follows:

{{< gist hellt d44b58c2f0c8b5f1be46047c9916aa82 >}}

This code has some extra additions to a simple two-step logic I mentioned before. I stuffed a default `data` value that will be used when the incoming request has no body, then we will use this dummy data just for demonstration purposes.  
To let me test the function code locally I added the `if __name__ == "__main__":` condition and lastly I wrote some `print` functions for a trivial logging. Speaking of which...

## 2.4 Logging
Logging is a bless! Having a chance to look what happens with your function in a cloud platform sandbox is definitely a plus. With GCP the [logging](https://cloud.google.com/functions/docs/monitoring/logging#functions-log-helloworld-python) can be done in the simple and advanced modes. A simple logging logs everything that is printed by a function into `stdout/stderr` outputs -> a simple `print()` function would suffice. In a more advanced mode you would leverage a GCP Logging API.

The logs can be viewed with the Web UI Logging interface, as well as with the `gcloud` CLI tool.

# 3 Function deployment
We previously already tried the deployed process with a boilerplate code just to make sure that the serverless framework works. Now that we have our `pycatj` package and its dependencies stored in a `vendored` folder and the function body is filled with the actual code, lets repeat the deployment and see what we get:

```
docker run --rm \
  -v ~/.gcloud/:/root/.gcloud \
  -v ~/projects/pycatj-web/pycatj-serverless:/opt/app \
  amaysim/serverless:1.45.1 serverless deploy
```
All goes well and serverless successfully updates our function to include the vendored artifacts as well as the new code in the `main.py`. Under the hood, the deployment process took the code of our Function and packaged it into a directory, zipped and uploaded to the deployment bucket.

As demonstrated above, the serverless framework allows a user to express the deployment in a code, making the process extremely easy and fast.

# 4 Usage examples
Time to give our Function a roll by bombing it with HTTP requests. In this section I will show you how you can use the pycatjify service within a CLI and in a subsequent post we will write a simple Web UI using the API that our function provides.
## 4.1 empty GET request
```python
curl -s https://us-central1-pycatj.cloudfunctions.net/pycatjify | jq -r .data

# returns
my_dict["data"] = "test_value"
my_dict["somenumber"] = 123
my_dict["a_dict"]["asd"] = "123"
my_dict["a_dict"]["qwe"][0] = 1
my_dict["a_dict"]["qwe"][1] = 2
my_dict["a_dict"]["qwe"][2] = 3
my_dict["a_dict"]["nested_dict"]["das"] = 31
my_dict["a_dict"]["nested_dict"]["qwe"] = "asd"
```
With an empty GET request the function delivers a demo of its capabilities by taking a hardcoded demo JSON and making a transformation. The returned string is returned in a JSON object accessible by the `data` key.

## 4.2 POST with a root and pycatj_data specified
Getting a demo response back is useless, to make use of a pycatjify service a user can specify the `root` value and pass the original JSON data in a POST request body using the `pycatj_data` key:
```bash
curl -sX POST https://us-central1-pycatj.cloudfunctions.net/pycatjify \
  -H "Content-Type: application/json" \
  -d '{"root":"POST","pycatj_data":{"somekey":"somevalue","a_dict":{"qwe":[1,2],"nested_dict":{"das":31}}}}' \
  | jq -r .data

# returns
POST["somekey"] = "somevalue"
POST["a_dict"]["qwe"][0] = 1
POST["a_dict"]["qwe"][1] = 2
POST["a_dict"]["nested_dict"]["das"] = 31
```

## 4.3 POST without root, with pycatj_data
It is also allowed to omit the `root` key, in that case a default root value will be applied:

```bash
curl -sX POST https://us-central1-pycatj.cloudfunctions.net/pycatjify \
  -H "Content-Type: application/json" \
  -d '{"pycatj_data":{"somekey":"somevalue","a_dict":{"qwe":[1,2],"nested_dict":{"das":31}}}}' \
  | jq -r .data

# returns
my_dict["somekey"] = "somevalue"
my_dict["a_dict"]["qwe"][0] = 1
my_dict["a_dict"]["qwe"][1] = 2
my_dict["a_dict"]["nested_dict"]["das"] = 31
```

## 4.4 POST with json file as a body
My personal favorite is dumping a JSON file in a request. In that case a lengthy `curl` is not needed and you can specify a path to a file with a `@` char.  
This example leverages the logic embedded in a function that treats the whole body of an incoming request as a data for `pycatj` transformation. 
```bash
$ cat test/test1.json
{
    "somekey": "localfile",
    "a_dict": {
        "asd": "123",
        "qwe": [
            1,
            2
        ],
        "nested_dict": {
            "das": 31,
            "qwe": "asd"
        }
    }
}

curl -sX POST https://us-central1-pycatj.cloudfunctions.net/pycatjify \
  -H "Content-Type: application/json" \
  -d "@./test/test1.json" \
  | jq -r .data

# returns
my_dict["somekey"] = "localfile"
my_dict["a_dict"]["asd"] = "123"
my_dict["a_dict"]["qwe"][0] = 1
my_dict["a_dict"]["qwe"][1] = 2
my_dict["a_dict"]["nested_dict"]["das"] = 31
my_dict["a_dict"]["nested_dict"]["qwe"] = "asd"
```

# What's next?
Having `pycatj` functionality available withing a HTTP call reach makes it possible to create a simple one-page web frontend that will receive the users input and render the result of the pycatj-web service we deployed in this post.

I will make another post covering the learning curve I needed to climb on to create a modern Material UI frontend that leverages the serverless function.

[[Project's source code](https://github.com/hellt/pycatj-web)]

> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>

> <style>.bmc-button img{height: 20px !important;width: 20px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 15px 7px 10px !important;line-height: 20px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 15px 7px 10px !important;font-size: 20px !important;letter-spacing:-0.08px !important;margin: 0 auto !important;font-family:'Lato', sans-serif !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/ntdvps"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px;font-size:14px !important;">For a coffee</span></a>