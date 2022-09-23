---
date: 2018-11-11
comments: true
keywords:
- Openstack
- Certification
tags:
- Openstack
- Certification

title: Prepping up for and passing the Certified Openstack Administrator Exam

---
Shortly after I passed [AWS CSA]({{<relref "aws_csa_certification.md">}}) exam I went on a hunt for the next certification to claim. Decided to tackle the [Openstack COA](https://www.openstack.org/coa) certification first saving the Docker/Kubernetes certification for a later occasion.

There is a common joke floating around: _"Oh, is Openstack still a thing?"_ - yes, its pretty much still a thing, especially in the Telecom area where VMs are the only viable option for the most of the cases (think VNFs).  
Openstack also powers our teams public SDN lab that allows to provision a fully functional Nuage environment in a matter of minutes. So I wanted to get a better operational knowledge of Openstack to be able to support and tune the platform if necessary.

Disclaimer: I took the recently updated COA exam which is based on the Openstack Pike release, although I did not face any Pike-specific questions during the exam. This does not mean that the exam content will stay the same throughout the course evolution, so watch out for the updates.

<!--more-->
## Key takeaways

Before going into detailed explanation of the preparation steps and the questions I found most challenging to prepare for, check out this list of COA key takeaways:

- Although it is a practice, scenario-based exam, its an easy one. You can prepare for it without being exposed to a production-grade Openstack operations.
- Focus on the questions that can't be done via Horizon, as they would eat most of the exam time.
- Use the Horizon all the time (unless the task assumes CLI approach); if you are not a CLI jockey I ensure you, you will loose the precious time.
- Make use of the embedded notebook to mark the questions left unfinished; you can get back to them later if time permits.
- Verify the connection requirements, as the exams virtual-room environment is sensible to a browser version and connection quality.
- Think of a backup internet connection.
- Clean the desk completely!

## Preparation

The exam is a relatively easy one; compared to [AWS CSA]({{<relref "aws_csa_certification.md">}}) it has far less material to learn and being a scenario-based exam it doesn't expect you to memorize things as you can wander in the Horizon dashboard working out a correct solution for the task.

> I actually liked the scenario-based approach more, it tests your hands-on skills rather than the ability to hold a lot of theory in your head (which wears off really fast anyway).

So how did I prepare for it? Being a LinuxAcademy user I first tried their COA courses, and they were completely useless. The course author spent 80% of the time in the CLI basically reading out load the CLI commands. Add on top the poor explanation of the basics and you get a perfect example of a bad course. So I do not recommend it to anyone.

When LinuxAcademy failed me on that front I went looking for a preparation book, remembering that [AWS CSA book](https://www.amazon.com/Certified-Solutions-Architect-Official-Study/dp/1119138558) was rather awesome. And found the one that I read cover-to-cover and can recommend to anyone looking for a single source of preparation: **Preparing for the Certified OpenStack Administrator Exam** by Matt Dorn. Here are the links where you can read/buy it:

- [Amazon](https://www.amazon.com/Preparing-Certified-OpenStack-Administrator-Exam-ebook/dp/B06WRT43DW)
- [Safaribooks](https://www.safaribooksonline.com/library/view/preparing-for-the/9781787288416/)
- [Packt](https://www.packtpub.com/virtualization-and-cloud/preparing-certified-openstack-administrator-exam)

In contrast to the online course I referred above, this book gives a really good theoretical background on the Openstack services that one would need to configure during the exam, supplementing it with the step-by-step configuration explanation. And yes, it also comes with a VirtualBox-based Openstack installation with pre-configured scenarios for each chapter.

### Horizon all the way

Although every exam study guide will most likely present you with the GUI and CLI ways of solving a particular task my recommendation is to solve everything in the Horizon, leaving CLI-specific tasks to the CLI.  
The reason is simple, a regular user will configure things much faster within Horizon dashboard, rather than copy-pasting UUIDs in an unfriendly CLI emulator.

There are tasks that can only be done within the CLI and these are the only ones that I recommend to solve with it.

### CLI-only tasks

There are tasks that has no way around but using the CLI to crack them. Tasks that require to interact with the objects like:

- `domains`
- `endpoints`,
- Downloading `glance` images
- Managing `swift` ACL rules and expiration dates

will require you to open the CLI, but these are the only tasks that will require it. The rest can be done much faster within the Horizon dashboard.

On the other hand I really encourage you to focus on these tasks, especially on the Swift's ACLs and object expiration tasks. Swift is the only service that will require you to use the `swift` CLI client instead of a common `openstack` CLI client. And to make your life harder there is no built-in help for `swift` commands to manage ACL and expiration, so **you need to memorize the exact commands**.

I also strongly suggest to pay additional attention to the tasks that test your ability to work with and analyze the Openstack Logs. You might make a mistake skipping it over, or paying a little attention to it.

### Troubleshooting tasks

Across the 40 scenarios that you would see during your exam there would be a troubleshooting section. As explained in the book I shared above you (most likely) will not see anything harder than the communication problem for a set of VMs. And the golden there rule is to check the Security Group rules to see if the rule is there and the protocol that must be working is set in the policy.

## Taking the exam

Now this is very important, if you dont want to be derailed by the proctor, make sure of the following:

### Desk stays clean

Clean the desk completely. I mean completely, nothing is allowed to be on the desk. The proctor gave me hard time asking me to clean the room and the desk. For the moment I thought that the proctor is actually my wife.

### Backup your internet link

If possible, have a backup internet connection. During the exam you would need to share your desktop, if you have >1 monitors you would need to share them all.  
For some mysterious reason, my perfect internet connection had been flagged as slow by the LinuxFoundation proctor and they asked me to provide another one, since the desktop stream was lagging.

Now this could caught you off-guard, I ended up setting up a mobile hot spot, so think about the backup.

### Intermittent connectivity is OK

Connection drops happened to me more than once; dont be scared, this is OK. You will be able to get back where you stopped, although the time could be only adjusted by the proctor.

### Using the integrated notebook

The exam environment allows you to use the integrated notebook. I used it to mark the questions that I left/skipped so I could come back to them later. Yes, you got it right, the exam environment does not mark which questions were unanswered, so you need to write down the question numbers for those which you unfinished.

## PS

Go and pursue the COA certification, its not the easiest one out there, but certainly its not one of the toughest. Depending on your exposure to the Openstack basics you can prepare only for the rare things like `swift` expiration configuration and maybe some other CLI-only tasks and sit the exam. Since it sports one free re-take, you can safely get a taste of it and probably pass it from the first attempt. Good luck!

![coa_cert](https://gitlab.com/rdodin/pics/-/wikis/uploads/11111cf64e2d44ece59a82837f1c4db6/image.png)

## Useful links

1. [Preparing for the Certified OpenStack Administrator Exam](https://www.amazon.com/Preparing-Certified-OpenStack-Administrator-Exam-ebook/dp/B06WRT43DW)
2. [Preparing to COA Git repo](https://github.com/PacktPublishing/Preparing-for-the-Certified-OpenStack-Administrator-Exam)
