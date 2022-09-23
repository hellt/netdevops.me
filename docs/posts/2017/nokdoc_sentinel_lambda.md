---
date: 2017-07-24
comments: true
keywords:
- AWS
- AWS Lambda
- AWS IAM
- AWS S3
- Boto3
- Python
- Serverless
tags:
- AWS
- AWS Lambda
- Boto3
- Python
- Serverless
title: Building AWS Lambda with Python, S3 and serverless

---

Cloud-native revolution pointed out the fact that the microservice is the new building block and your best friends now are Containers, AWS, GCE, Openshift, Kubernetes, you-name-it. But suddenly _micro_ became not that granular enough and people started talking about _serverless functions_!
{{< image classes="center fancybox clear" src="https://lh3.googleusercontent.com/iNjG1IpPyFKkXIsJThti5hs7_Ytc7GGpf4rCUCw5-f0dF31BYWbyyW3In1Fh4PvTKyh8xamSMKxMeFx6unzqao4ouLPxueLpx8RGD5Fg4SM2Kp_plaryC7zuUsRmAZ8-W9mHwzyuQQmC11-FH-yF5ef1FPsh0xglVv4IcSRDSPUO0BuqNZF0Vd5LpvgRGOvmE0xeqFoK-uUlM0KXRIFQusIcscq-Vv6SVKMBahoOpkhorTFCPD1tAIo4a6-q7diwWJj6TPWMnhMfg85s-NSz_0MR7bTIWw_PRN3HM66sfe8X3a7lmEuc1KxJ1ZF20qS6b9rW90Pa2iw6mHk_b_IjBBQBYeRScTgXd7IZpRQlO5-28RKvSvSJTxoSiCLBIuCgYebgp5hF62w_3Rmd9ajV3fEi_BMT04vd5gft5Mzad0NIA-sDboETXHM-n0UBnvvToAzENmfTl6pC9dXfaXlAvVqDRwDWmXjD5EGnIhLH-6lLSzswlNgqpZYDqd20p0cz_0-8xxmdXrdp7WyHCO4NMkpgZa6zvPpJipPRIaTImqr-GhaceBEHWzFF27aNQ6bx6FNXHj4IhfnM1VyuDqTU33-De-kft_IUF27g6XNKA41ytnNvstOSTqwEFA=w638-h359-no" title="Brian Christner, Docker & Serverless: <https://www.slideshare.net/BrianChristner/docker-serverless>" >}}

When I decided to step in the serverless property I chose [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html) as my instrument of choice. As for experimental subject, I picked up one of my existing projects - a script that tracks new documentation releases for Nokia IP/SDN products (which I aggregate at [nokdoc.github.io](https://nokdoc.github.io)).

Given that not so many posts are going deeper than onboarding a simplest function, I decided to write down the key pieces I needed to uncover to push a **real code** to the Lambda.

Buckle up, our agenda is fascinating:

- testing basic Lambda onboarding process powered by Serverless framework
- accessing files in AWS S3 from within our Lambda with `boto3` package and custom AWS IAM role
- packaging non-standard python modules for our Lambda
- exploring ways to provision shared code for Lambdas
- and using path variables to branch out the code in Lambda

<!--more-->

# Init

What I am going to _lambdsify_ is an existing python3 script called **nokdoc-sentinel** which has the following Lambda-related properties:

- uses non standard python package -- `requests`
- reads/writes a file.

I specifically emphasized this non-std packages and relying on persistence since these aspects are not covered in 99% of Lambda-related posts, so, filling the spot.

> AWS Lambda is a compute service that lets you run code without provisioning or managing servers. AWS Lambda executes your code only when needed and scales automatically, from a few requests per day to thousands per second.

Multiple choices are exposed to you when choosing an instrument to configure & deploy an AWS Lambda:

- AWS Console (web)
- AWS CLI
- Multiple frameworks ([Serverless](https://serverless.com/), [Chalice](https://chalice.readthedocs.io/en/latest/index.html), [Pywren](http://pywren.io/))

While it might be good to feel the taste of a manual Lambda configuration process through the AWS Console, I decided to go "everything as a code" way and use the [Serverless](https://serverless.com/) framework to define, configure and deploy my first Lambda.

> The **Serverless Framework** helps you develop and deploy your AWS Lambda functions, along with the AWS infrastructure resources they require. It's a CLI that offers structure, automation and best practices out-of-the-box, allowing you to focus on building sophisticated, event-driven, serverless architectures, comprised of Functions and Events.

# Serverless installation and configuration

First things first, [install](https://serverless.com/framework/docs/providers/aws/guide/installation/) the framework and [configure AWS credentials](https://serverless.com/framework/docs/providers/aws/guide/credentials/). I already had credentials configured for AWS CLI thus skipped that part, if that is not the case for you, the docs are comprehensive and should have you perfectly covered.

# Creating a Service template

Once serverless is installed, start with creating an `aws-python3` service:

> A `service` is like a project. It's where you define your AWS Lambda Functions, the events that trigger them and any AWS infrastructure resources they require, all in a file called serverless.yml.

```bash
serverless create --template aws-python3 --name nokdoc-sentinel
```

Two files will be created:

- `handler.py` -- a module with Lambda function boilerplate code
- `serverless.yml` -- a service definition file

# Making lambda instance out of a template

I renamed `handler.py` module to `sentinel.py`, also changed the enclosed function' name and deleted redundant code from the template. For starters I kept the portion of a sample code just to test that deploying to AWS via serverless actually works.

```python
# sentinel.py
import json

def check(event, context):
    body = {
        "message": "Sentinel is on watch!",
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
```

Thing to remember is that you also must to make appropriate changes in the `serverless.yml`, once you renamed the module and the function names:

```bash
functions:
# name of the func in the module
  check:
    # `handler: sentinel.check` reads as 
    # "`check` function in the `sentinel` module
    handler: sentinel.check
```

## Deploying and Testing AWS Lambda

Before adding some actual load to the Lambda function, lets test that the deployment works. To trigger Lambda execution I added **HTTP GET** [event](https://serverless.com/framework/docs/providers/aws/guide/events/) with the `test` path in the `serverless.yml` file. So a call to `https://some-aws-hostname.com/test` should trigger our lambda function to execute.

```bash
functions:
  hello:
    handler: handler.hello
    # add http GET trigger event
    events:
      - http:
          path: test
          method: get
```

> Read all about supported by serverless framework events in the [official docs](https://serverless.com/framework/docs/providers/aws/guide/events/).

And we are coming to the first test deployment with the following assets:

```bash
$ tree -L 1
.
|-- sentinel.py
`-- serverless.yml
```

Lets go and deploy:

```
$ serverless deploy
Serverless: Packaging service...
Serverless: Creating Stack...
Serverless: Checking Stack create progress...
.....
Serverless: Stack create finished...
Serverless: Uploading CloudFormation file to S3...
Serverless: Uploading artifacts...
Serverless: Uploading service .zip file to S3 (0.33 MB)...
Serverless: Validating template...
Serverless: Updating Stack...
Serverless: Checking Stack update progress...
..............................
Serverless: Stack update finished...
Service Information
service: nokdoc-sentinel
stage: dev
region: us-east-1
api keys:
  None
endpoints:
  GET - https://xxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/test
functions:
  check: nokdoc-sentinel-dev-check
```

Note the endpoint URL at the bottom of the output, using this API endpoint we can check if our Lambda is working:

```bash
curl https://xxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/test
{"message": "Sentinel is on watch!"}
```

# Exploring Serverless artifacts

Serverless deployed the Lambda using some defaults parameters (region: us-east-1, stage: dev, IAM role); plus serverless did some [serious heavy-lifting](https://serverless.com/framework/docs/providers/aws/cli-reference/deploy#how-it-works) in order to deploy our code to AWS. In particular:

- archived the project files as a zip archive and loaded it to AWS S3
- created CloudFormation template that defines all the steps needed to onboard a Lambda and setup an API gateway to respond to `GET` requests

Key artifacts that were created by serverless in AWS can be browsed with the AWS CLI:

```bash
# exploring deployed Lambda
$ aws --region us-east-1 lambda list-functions
{
    "Functions": [
        {
            "FunctionName": "nokdoc-sentinel-dev-check",
            "FunctionArn": "arn:aws:lambda:us-east-1:446595173912:function:nokdoc-sentinel-dev-check",
            "Runtime": "python3.6",
            "Role": "arn:aws:iam::446595173912:role/nokdoc-sentinel-dev-us-east-1-lambdaRole",
            "Handler": "sentinel.check",
            "CodeSize": 1395199,
            "Description": "",
            "Timeout": 6,
            "MemorySize": 1024,
            "LastModified": "2017-07-17T19:06:59.405+0000",
            "CodeSha256": "QrFOl8eBL8HipGRCkN/P7wsxkn8/LDIMCAQLxAVmFfI=",
            "Version": "$LATEST",
            "TracingConfig": {
                "Mode": "PassThrough"
            }
        }
    ]
}


# exploring S3 artifacts
$ aws s3 ls | grep sentinel
2017-07-17 22:05:13 nokdoc-sentinel-dev-serverlessdeploymentbucket-moviajl407hw

$ aws s3 ls nokdoc-sentinel-dev-serverlessdeploymentbucket-moviajl407hw/serverless/nokdoc-sentinel/dev/1500318307598-2017-07-17T19:05:07.598Z/
2017-07-17 22:05:40       3578 compiled-cloudformation-template.json
2017-07-17 22:05:41    395199 nokdoc-sentinel.zip

# exploring CloudFormation stack
$ aws --region us-east-1 CloudFormation list-stacks
{
    "StackSummaries": [
        {
            "StackId": "arn:aws:cloudformation:us-east-1:446595173912:stack/nokdoc-sentinel-dev/da010710-6b22-11e7-aa95-500c20fef6d1",
            "StackName": "nokdoc-sentinel-dev",
            "TemplateDescription": "The AWS CloudFormation template for this Serverless application",
            "CreationTime": "2017-07-17T19:05:08.875Z",
            "LastUpdatedTime": "2017-07-17T19:05:45.283Z",
            "StackStatus": "UPDATE_COMPLETE"
        }
    ]
}
```

Are you interested what is in this archive `nokdoc-sentinel.zip`?

```bash
$ ls -la ~/Downloads/nokdoc-sentinel/
total 16
drwx------@  6 romandodin  staff   204 Jul 18 09:51 .
drwx------+ 54 romandodin  staff  1836 Jul 18 09:51 ..
drwxr-xr-x@  3 romandodin  staff   102 Jul 18 09:51 .vscode
-rw-r--r--@  1 romandodin  staff   208 Jan  1  1980 sentinel.py
-rw-r--r--@  1 romandodin  staff  3720 Jan  1  1980 watcher.py
```

There are two files we dealt with earlier plus `.vscode` dir that a text editor created for its settings. Having `.vscode` in the deployment package actually indicates that by default serverless zipped everything in the project' dir. You can get in control of this process by using [include/exclude statements](https://serverless.com/framework/docs/providers/aws/guide/packaging#package-configuration).

# Accessing AWS S3 from within a Lambda

It is natural that AWS assumes that Lambdas will be used in a close cooperation with the rest of the AWS family. And for the file storage **AWS S3** is a one-stop shop.

## Sorting out permissions

What you have to sort out before digging into S3 interaction is the permissions that your Lambda has. When serverless deployed our Lambda with a lot of defaults it also handed out a [default IAM role](https://serverless.com/framework/docs/providers/aws/guide/iam/#the-default-iam-role) to our Lambda:

```bash
aws --region us-east-1 lambda list-functions | grep Role
            # role name is nokdoc-sentinel-dev-us-east-1-lambdaRole
            "Role": "arn:aws:iam::446595173912:role/nokdoc-sentinel-dev-us-east-1-lambdaRole",
```

To be able to interact with AWS S3 object model, this Role should have access to S3. Lets investigate:

```bash
aws iam get-role-policy --role-name nokdoc-sentinel-dev-us-east-1-lambdaRole --policy-name dev-nokdoc-sentinel-lambda
{
    "RoleName": "nokdoc-sentinel-dev-us-east-1-lambdaRole",
    "PolicyName": "dev-nokdoc-sentinel-lambda",
    "PolicyDocument": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "logs:CreateLogStream"
                ],
                "Resource": [
                    "arn:aws:logs:us-east-1:446595173912:log-group:/aws/lambda/nokdoc-sentinel-dev-check:*"
                ],
                "Effect": "Allow"
            },
            {
                "Action": [
                    "logs:PutLogEvents"
                ],
                "Resource": [
                    "arn:aws:logs:us-east-1:446595173912:log-group:/aws/lambda/nokdoc-sentinel-dev-check:*:*"
                ],
                "Effect": "Allow"
            }
        ]
    }
}
```

As you see S3 access is not a part of default permissions, so we must grant it to our Lambda. Instead of adding additional permissions to the existing role manually, we can re-deploy the Lambda with updated `serverless.yml` file. In this edition I specified availability zone, set existing S3 bucket as a deployment target and included IAM role configuration allowing full-access to S3 objects:

```bash
# serverless.yml
provider:
  name: aws
  runtime: python3.6
  stage: dev
  region: eu-central-1
  # deploy Lambda function files to the bucket `rdodin`
  deploymentBucket: rdodin
  # IAM Role configuration to allow all-access for S3 objects of bucket `rdodin`
  iamRoleStatements:
    - Effect: "Allow"
      Action: "s3:*"
      Resource: "arn:aws:s3:::rdodin/*"
```

Now the re-deployment will create another Lambda (hence the availability zone has changed), deploy the code in the existing bucket `rdodin` and apply a policy that allows S3 interaction.

```bash
# checking the inline policy of the IAM Role bound to Lambda
aws lambda get-function --function-name nokdoc-sentinel-dev-check | grep Role
        "Role": "arn:aws:iam::446595173912:role/nokdoc-sentinel-dev-eu-central-1-lambdaRole",

aws iam list-role-policies --role-name nokdoc-sentinel-dev-eu-central-1-lambdaRole
{
    "PolicyNames": [
        "dev-nokdoc-sentinel-lambda"
    ]
}

aws iam get-role-policy --role-name nokdoc-sentinel-dev-eu-central-1-lambdaRole --policy-name dev-nokdoc-sentinel-lambda
{
    "RoleName": "nokdoc-sentinel-dev-eu-central-1-lambdaRole",
    "PolicyName": "dev-nokdoc-sentinel-lambda",
    "PolicyDocument": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "logs:CreateLogStream"
                ],
                "Resource": [
                    "arn:aws:logs:eu-central-1:446595173912:log-group:/aws/lambda/nokdoc-sentinel-dev-check:*"
                ],
                "Effect": "Allow"
            },
            {
                "Action": [
                    "logs:PutLogEvents"
                ],
                "Resource": [
                    "arn:aws:logs:eu-central-1:446595173912:log-group:/aws/lambda/nokdoc-sentinel-dev-check:*:*"
                ],
                "Effect": "Allow"
            },
            {
                "Action": "s3:*",
                "Resource": "arn:aws:s3:::rdodin/*",
                "Effect": "Allow"
            }
        ]
    }
}
```

Now as the S3 permissions are there, we are free to list bucket contents and modify the files in it.

## Using Boto3 to read/write files in AWS S3

AWS provides us with the [boto3](https://boto3.readthedocs.io/en/latest/index.html) package as a Python API for AWS services. Moreover, this package comes pre-installed on the [system that is used to run the Lambdas](https://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html), so you do not need to provide a package.

I put a file _(releases\_current.json)_ that my script expects to read to the directory created by the serverless deployment script:

```bash
$ aws s3 ls rdodin/serverless/nokdoc-sentinel/
                           PRE dev/
2017-07-22 15:57:07       3424 releases_current.json
```

Lets see if we can access it from within the Lambda using `boto3` and its [documentation](https://boto3.readthedocs.io/en/latest/reference/services/s3.html):

```python
# sentinel.py
import json
import boto3


def check(event, context):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('rdodin')
    # reading a file in S3 bucket
    original_f = bucket.Object(
        'serverless/nokdoc-sentinel/releases_current.json').get()['Body'].read()[:50]
    # writing to a file
    new_f = bucket.put_object(
        Key='serverless/nokdoc-sentinel/newfile.txt', Body='Hello AWS').get()['Body'].read()

    body = {
        "message": "Sentinel loaded a file {} and created a new file {}"
        .format(original_f, new_f),
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
```

Re-deploy and check:

```bash
$ curl https://xxxxx.execute-api.eu-central-1.amazonaws.com/dev/test
{"message": "Sentinel loaded a file b'{\"nuage-vsp\": [\"4.0.R8\", \"4.0.R7\", \"4.0.R6.2\", \"4.' and created a new file b'Hello AWS'"}
```

So far, so good. We are now capable of reading/writing to a file stored in AWS S3.

# Adding python packages to Lambda

We were lucky to use only the packages that either standard (`json`) or comes preinstalled in Lambda-system (`boto3`). But what if we need to use packages other from that, maybe your own packages or from PyPI?

Well, in that case you need to push these packages along with your function' code as a singe _deployment package_. [As official guide says](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html) you need to copy packages to the root directory of your function and zip everything as a single archive.

What comes as a drawback of this recommendation is that

- your project dir will be dirty with all these packages sitting in the root
- you will have to .gitignore these packages directory to keep your packages out of a repository

I like the solution proposed in the ["Building Python 3 Apps On The Serverless Framework"](https://serverlesscode.com/post/python-3-on-serverless-framework/) post. Install your packages in a some directory in your projects dir and modify your `PYTHONPATH` to include this directory.

```bash
# install `requests` package in a `vendored` dir at the projects root
pip install -t vendored/ requests

# `requests` and its dependencies are there
$ ls vendored/
certifi                     chardet                     idna                        requests                    urllib3
certifi-2017.4.17.dist-info chardet-3.0.4.dist-info     idna-2.5.dist-info          requests-2.18.1.dist-info   urllib3-1.21.1.dist-info
```

Now modify your code to include `vendored` directory in your `PYTHONPATH`

```python
import boto3

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "vendored"))
# now it is allowed to add a non-std package
import requests

def check(event, context):
# output omitted
```

Note, that if a package has a native binary code, it must be compiled for [the system that is used to run Lambdas](https://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html).

# Shared code for Lambdas

Even though a Lambda often assumed as an independent function, a real application you might want to transfer to Lambda quite likely will have dependencies on some common code. Refer to the ["Writing Shared Code"](https://serverlesscode.com/post/python-3-on-serverless-framework/#writing-shared-code) section of the above mentioned blog post to see how its done.

# Handling arguments in Lambdas

Another common practice in a classic util function is to have some arguments (argparse) that allow to branch out the code and make an app' logic feature-rich. In Lambdas, of course, you have no CLI exposed, so to make a substitution for the arguments you can go two ways:

- create several functions for your project and bind different API endpoints to each of them
- use a single function and add a variable part to the API endpoint

I will show how to handle the latter option. First, create a variable parameter for your API endpoint in the `serverless.yml`:

```bash
    events:
      - http:
          # `{command}` is a variable part here
          path: go/{command}
          method: get
```

Now you Lambda can be branched out like that, using the part that you will place in the end of your API endpoint as an argument.

```python
def check(event, context):
    # a variable that we referenced as {command} in serverless.yml
    # can be accessed by a `command` key of event['pathParameters'] dict
    if 'branch1' in event['pathParameters']['command']:
        body = {
            "message": "Argument `A` execution block"
        }

    if 'branch2' in event['pathParameters']['command']:
        body = {
            "message": "Argument `B` execution block"
        }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
```

Now adding an arbitrary text after the `go/` path will be evaluated in your Lambda allowing you to conditionally execute some parts of your code.

# Summary

With the above explained concepts I successfully transferred **nokdoc-sentinel** script from a standalone cron-triggered module to the AWS Lambda. You can check out the project' code and the `serverless.yml` file at [github repo](https://github.com/hellt/nokdoc-sentinel-lambda).

# Links

1. **Benny Bauer** -- [Python in The Serverless Era PyCon 2017](https://www.youtube.com/watch?v=G17E4Muylis)
1. **Ryan S. Brown** -- [Building Python 3 Apps On The Serverless Framework](https://serverlesscode.com/post/python-3-on-serverless-framework/)
1. [Serverless Framework AWS Guide](https://serverless.com/framework/docs/providers/aws/guide/)
1. [AWS Lambda Developers Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
1. [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/reference/)
1. [Keeping secrets out of Git with Serverless](http://www.goingserverless.com/blog/keeping-secrets-out-of-git)

> Post comments [are here](https://gitlab.com/rdodin/netdevops.me/issues/2).
