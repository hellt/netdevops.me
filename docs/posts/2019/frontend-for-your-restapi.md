---
title: Creating a Bootstrap based front-end for your simple REST service
date: 2019-07-28T09:00:07+00:00
author: Roman Dodin
comment_id: frontend-for-rest
keys:
  - javascript
  - frontend
  - bootstrap
tags:
  - javascript
  - frontend
  - bootstrap
---

Not a single day goes by without me regretting I haven't mastered any front-end technology like React/Angular or the likes.  Why would a network engineer want to step into the game that seems orthogonal to its main area of expertise, one might ask?

Truth be told, I wasn't born with an urge to learn anything that has _javascript_ under the hood, but over the years, working within the network/backend silos, I realized, that being able to create a simple front-end service is a jewel that fits every crown, no matter what title you wear.

This tutorial is based on the task real task of building up a web interface ([pycatjify.netdevops.me](https://pycatjify.netdevops.me)) for the [`pycatjify`](../creating-google-cloud-platform-function-with-python-and-serverless/) REST API service deployed as a serverless function. The end result is a **simple**, completely **free** and **reusable** Bootstrap based front-end boilerplate which can be used as a foundation for a similar task.

<!--more-->

## 1 Benefits of knowing how to front-end?
Lets me first explain why I think that even a basic experience with any front-end technology is beneficial to virtually anyone.

### 1.1 Get your tool a web interface

We often start with an idea of a tool and work it to a completion by publishing a command line interface to it, sometimes the CLI is all the tool needs, it is just best consumed that way. Other times even the CLI is not needed, as the tool is only used as a plugged-in library.

But quite often the tool can benefit greatly by having its own web interface. You can broaden the horizons of your project audience vastly by simply creating a web service out of it. I can name a handful number of tools that I consume via web instead of using their CLI counterparts, it is just more convenient to me and so might think the users of your tools.

The [`pycatj`](https://github.com/dbarrosop/pycatj/) is a perfect example of a CLI-first tool that can be conveniently consumed via web as well. Thus I set myself on a journey to create a web facade for it and at the same time reinforcing my very basic web skills.

### 1.2 Take your pitch or demo to a next level
Not everyone of us is working in an environment where the bosses have engineering background and can equally enjoy a demo of a new service by looking at the terminal full of `curl` requests. Even if your bosses are the ones who contribute to the cutting edge technologies, your customers can easily be made of a different dough.

Therefore it might be equally important to supplement your neat idea with a proper visualization; my experience says that a great tool or a service attracts audience way better when it is wrapped in a shiny package. So having a prototyped web UI might give you some bonus points even if it is not going to be consumed via the Web UI after all.

### 1.3 Learn how they do it on the other side of a fence
A classic, book-pictured network automation engineer is an all Python-shop customer. Although Python is a natural fit for the network automation activities, it is also important to not less yourself be constrained by a singe language or a toolchain.

Educating yourself on a different technology with a different set of the instruments and/or the views means a lot. Even by scratching the surface of the Javascript, its package managers and the front-end frameworks could make you better understand the pros and cons of the ecosystem you are in.

## 2 Front-end & Javascript frameworks
![pic](https://gitlab.com/rdodin/pics/-/wikis/uploads/6e95f9e54f4062d13e314fc1b4d78266/image.png)

So how do one start if they want to learn any of that shiny front-end witchery given that there are so many frameworks around? In spite to answer this question I compiled the following list of options that when I approached the task of making a [`pycatjify`](https://pycatjify.netdevops.me) web service:

1. **Frameworkless: bare HTML/CSS/JS**  
This is the most straightforward way of creating a web service. You basically write everything by yourself without relying on any framework.  
On the _pros_ side this is the most lightweight and bloat-less approach, as you are in the full control of what contributes to the end result.  
The _cons_ side is substantial though, you need to be well experienced in the HTML/CSS/JS to create something less minimalistic than a blank page with the elements on it.

1. **Front-end frameworks**  
Front-end frameworks provide a shortcut for a web service creation drastically reducing time to create one. Also known as CSS frameworks they come across with the lego-like blocks (components implemented with CSS/JS/HTML) that you use to build a web service from.  
Dozens of front-end frameworks have been created over the time, from the minimalistic ones to the monstrous software bundles.  
[Bootstrap](https://getbootstrap.com), [Foundation](https://foundation.zurb.com/), [Skeleton](http://getskeleton.com/), [Materialize](https://materializecss.com/) are one of the few that one can find in the numerous "top front-end frameworks" charts.  
A major benefit that all above mentioned frameworks share is that they don't need to be compiled and can be run by all modern browsers. All it takes is to put the framework' HTML/CSS/JS files along with your project and open the `index.html`.

1. **Javascript frameworks and libraries: React/Angular/Vue/etc**  
These are the modern age Javascript frameworks (often referred as libraries) that enable you to build modern web/mobile applications with a feature-rich logic. With the great power, though, comes the great size and complexity; installing a sample React app can easily add thousands of JS packages that framework depends on.  
The learning curve for these frameworks is steep as opposed to the front-end frameworks listed in [2]. But mastering one of them would enable you to create versatile and breathtaking Web UIs as well as mobile applications.  
Notable frameworks in that category are [React](https://reactjs.org/), [Vue](https://vuejs.org), [Angular](https://angular.io/), [Ember](https://emberjs.com/).

Since I am not a front-end developer the sweet spot for me lies with the front-end frameworks that I can install/run without a specific harness. They are lightweight, easy to work with, and all it takes to start is the basic HTML/CSS/JS knowledge. At the same time they provide just enough features to handle not overly complicated tasks a network engineer might encounter in a small size projects.

For the [pycatjify.netdevops.me](https://pycatjify.netdevops.me) I decided to use a "Material Design" flavored Bootstrap based framework called [mdboostrap](https://mdboostrap.com).

> Also I had some past experience with the Bootstrap 3 framework when I worked on [a Web UI for the python scripts](https://netdevops.me/2016/04/building-web-front-end-for-python-scripts-with-flask/) quite some time ago.

## 3 Mdbootstrap
![mdb logo](https://mdbootstrap.com/wp-content/uploads/2018/06/logo-mdb-jquery-small.png)
Mdbootstrap (MDB) offers the Material-UI themed components for the various JS frameworks such as Bootstrap/JQuery, Angular, React and Vue. For the reasons outlined in section 2, I decided to go with a [Bootstrap/JQuery version](https://mdbootstrap.com/docs/jquery/) of the MDB framework as this is the easiest way to put up a simple front-end service for me.

> MDB offers a free [quick start guide](https://mdbootstrap.com/education/bootstrap/quick-start/) as well as a [full-length](https://mdbootstrap.com/education/bootstrap/) tutorial if you want to refresh the bootstrap basics or follow an authored paid course.

> Bootstrap popularity also makes it extremely easy to find a lot of guides and tutorials that tremendously help to understand the basics of this framework.

MDB, being based on the Bootstrap 4, obviously follows its ancestors paradigms when it comes to the Grid system, CSS, components, etc. If you worked with the Bootstrap before then the MDB won't be a problem at all. Moreover, the elements I used in this project are not MDB specific, the same components are available in the original Bootstrap library.

### 3.1 Install the framework
Its extremely easy to "install" mdbootstrap/bootstrap framework, its hardly an installation even, as all you need is to [download](https://mdbootstrap.com/docs/jquery/getting-started/download/) the archive and extract the framework' files. Once done, the framework contents is nothing more than a small number of the folders and files:

```bash
.
├── [drwxr-xr-x]  css
├── [drwxr-xr-x]  font
├── [drwxr-xr-x]  img
├── [drwxr-xr-x]  js
├── [drwxr-xr-x]  scss
└── [-rwxr-xr-x]  index.html

5 directories, 4 files
```

Yes, thats literally all you need, no packages installation no dependency management, just static files, classy! You can open the `index.html` with your browser and it'll just work.

### 3.2 Framework structure
The framework comes with the following important components that make it all work in a unison to display the web page built with it:

* CSS files in the `css` folder that define the styling of the framework elements and controls
* Javascript files in the `js` folder that comprise the dynamic logic that the framework relies on
* Static images in the `img` folder as well as the fonts in the `font` directory
* Index HTML file that in a simple case will have all the website contents

Take a look at the `index.html` file that comes with a framework:

{{< gist hellt f0878010813c21837a518d89f36f5e61 >}}

In the [`<head>`](https://gist.github.com/hellt/f0878010813c21837a518d89f36f5e61#file-index-html-L4-L17) section of this HTML file the CSS files are being loaded. These CSS files comprise a big portion of the framework itself, as they govern the styling that the components have.

Then the [`<body>`](https://gist.github.com/hellt/f0878010813c21837a518d89f36f5e61#file-index-html-L19-L44) section of the HTML file holds the default web page's content.  
The `index.html` file that comes with a template has a `div` with a few headers and a paragraph of text. You will replace then with the framework components like Navigation bars, input forms, tables, text elements, modal dialogs when you start to build your front-end service.

In the [ending](https://gist.github.com/hellt/f0878010813c21837a518d89f36f5e61#file-index-html-L35-L43) of the `<body>` section you would find the `<script>` elements that load the Javascript code the framework relies on. The custom JS code that your service most likely will have will also be added in the body's tail section (see [section 4](#4-hooking-up-the-back-end) for an example).

### 3.3 Bootstrap components are your lego blocks
The framework's library has a lot of components that might be treated like the lego blocks with which you build the web facade. The benefit of having the pre-created components is huge; you don't need to create these common components yourself from the ground up, just browse the library and pick the right ones.

> ![components](https://gitlab.com/rdodin/pics/-/wikis/uploads/cb491f0ab8842f37bcd76f8557102d72/image.png)
> <center><small>Example of the tabs & pills components</small></center>

To understand which components I'd need for the pycatjify I imagined what layout would I want my page to have. Since `pycatj` is a tool that works on an input JSON/YAML data and produces a multi line output, the simple layout could consist of a [navigation bar](https://mdbootstrap.com/docs/jquery/navigation/navbar/) with the project logo, the two [input fields](https://mdbootstrap.com/docs/jquery/forms/inputs/) for input and output data and the [modal dialog](https://mdbootstrap.com/docs/jquery/modals/basic/) with [cards](https://mdbootstrap.com/docs/jquery/components/cards/).

Knowing the needed basic building blocks we can now browse the framework' [documentation](https://mdbootstrap.com/docs/jquery/) section in search for the right ones. The MDB docs are just great for that - lots of examples on how to use the various components in different kinds of shapes and sizes. Basically you copy the example from the docs, paste it to your HTML file and tune it as per the components options which are explained in the docs.

When building pycatjify front-end I just removed the default contents of the `<body>` section of the `index.html` file and started to throw in the components as per the layout I had in my head. Thats what the [`index.html`](https://github.com/hellt/pycatj-web/blob/master/pycatj-web/index.html) for the [pycatjify.netdevops.me](https://pycatjify.netdevops.me) started to look like when I added all the components I talked above.

It looks like a lot of lines of code, but everything was just pasted from the examples section. First time it takes some time to get to know the components and their behavior, but do it once and the next project would be an effortless task.

> ![pic](https://gitlab.com/rdodin/pics/-/wikis/uploads/6a42e976d4a8a732b6b62f1e2f58a7dd/image.png)
> <center><small>pycatjify web ui</small></center>

## 4 Hooking up the back-end
As implied by the name of this post, the communication between the front-end and the back-end is happening using the REST API. In the [previous post](../creating-google-cloud-platform-function-with-python-and-serverless/) I wrote about the way I packaged the [`pycatj`](https://github.com/dbarrosop/pycatj/) tool into a Google Cloud Function which exposes a single API endpoint. Now it is time to make our front-end to be a REST API client that talks to the back-end and displays the results it receives back.

This is a breakdown of a communication logic between the front and back ends:

1. Capture the user input (which is a YAML or JSON formatted text) from the input field
2. Send it via `HTTP POST` request to the back-end API endpoint in a JSON format
3. Back-end to receives a request and does the transformation of the received data
4. It then sends the transformed data back as a string packed in a JSON body as well.

### 4.1 REST API client with JQuery/AJAX
There are several ways of making an asynchronous HTTP request from within the front-end service. One approach would be by using the JQuery's [AJAX](https://api.jquery.com/jquery.ajax/) function. Since MDB framework has JQuery as its dependency and this library is already loaded into our page we can use it right away.

Lets add a Javascript file at the `js/pycatjify.js` path that will implement the logic of a REST client.

{{< gist hellt 93154da758722192beca0fdf80d53b3a >}}

This little unnamed function is bound to the [button](https://github.com/hellt/pycatj-web/blob/master/pycatj-web/index.html#L76) with id `convert_btn` by the means of the `#convert_btn` selector. Specifically to its `click` action. That means that when a click action occurs on the `convert_btn` button, this JS code kicks in.

In the very beginning the code reads the data from the input element text area into the `data["pycatj_data"]` object. Next, it serializes the variable value into the JSON string since we chose to use JSON payload with our POST request.

And then the actual AJAX request (which is essentially a JQuery name for the async HTTP call) comes into play:

```js
$.ajax({
    url: "https://us-central1-pycatj.cloudfunctions.net/pycatjify",
    contentType: "application/json",
    data: body,
    dataType: "json",
    type: 'POST',
    success: function (response) {
        $('#out_form').val(response.data)
    }
});
```

* With the `url` parameter we say what is the URL of our REST API endpoint
* `contentType` set to `application/json` narrows down the type of the content we will convey through HTTP messages
* the `data` that we send with this specific request is contained in the `body` variable computed [before](https://gist.github.com/hellt/93154da758722192beca0fdf80d53b3a#file-pycatjify-js-L14)
* `dataType: "json"` allows us to treat the returned response as the JSON object, and since our pycatj serverless function returns the JSON it is exactly what we need.
* the request `type` is `POST`

If our POST request succeeds and we receive a `response`, we call a function that displays the results received as a JSON. Because of our serverless function returns the data in a `data` field, we select this field with the `response.data` selector in the `$('#out_form').val(response.data)` expression.

## 5 Hosting the web application
Since our back-end code is hosted by a GCP Function, the front-end itself is nothing more than a bunch of static files (CSS, JS, HTML), and that means that it can easily be hosted **for free** with the beautiful [Gitlab Pages](https://docs.gitlab.com/ee/user/project/pages/) service.

For that I added a [`.gitlab-ci.yml`](https://github.com/hellt/pycatj-web/blob/master/.gitlab-ci.yml) file that has a single `pages` job responsible for copying the web service related files to the `public` directory which, in its turn, tells Gitlab to start serving these files over HTTP.

Now with every push to the master branch Gitlab will restart the web server to ensure that the most recent files are being served. 

## 6 Summary
This pretty much concludes the Minimum Viable Product of the web front-end for the simple REST API service:

* by leveraging the Google Cloud PLatform Functions we [deployed](../creating-google-cloud-platform-function-with-python-and-serverless/) a python code that implements a back-end REST API service - **$0**
* the front-end is built with a simple Bootstrap/JQuery based [MDB](https://mdboostrap.com) framework and hosted with Gitlab Pages - **$0**
* the wildcard TLS certificate is provided by Cloudflare - **$0**

As you see, the process of putting a simple front-end service is simple and completely free. It goes without saying, that the example presented in this topic uses a very basic layout and a straightforward design - hence the overall simplicity. For instance the it does not handle any errors and does not perform input validation. Adding the spinner element to the UI to indicate the processing time would also enhance the UX.  
You can imagine, that adding all of these features increases the complexity of the code base and might require additional components and/or libraries.

I hope this "how to create a front-end being not a front-ender" post helps you with the basics of a simple front-end machinery. Remember, its important to start, and its easier to start small, you can always grow later. And I think the Bootstrap-like frameworks are a good choice for that.

Checkout the [project's source code](https://github.com/hellt/pycatj-web) and leave the comments or ask questions below if I missed something.

