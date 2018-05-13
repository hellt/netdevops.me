---
date: 2018-05-11T12:00:00Z
keywords:
- AWS
- Certification
tags:
- AWS
- Certification

title: Prepping up for and passing the AWS Certified Solution Architect - Associate

---

On May 11th I passed the [AWS Certified Solution Architect Associate](https://aws.amazon.com/certification/certified-solutions-architect-associate/) exam which was harder then I expected. In this memo I will outline how I prepared to this exam, what topics you better pay more attention to and some tips and hints I could give to anyone going for AWS CSA exam.

Disclaimer: I took the original AWS CSA exam, not the one that was launched in Feb 2018; this older version is only available to schedule till August 2018. After that date the newer version of this exam will be the only one available. Watch out, it [has a new set of objectives](https://d1.awsstatic.com/training-and-certification/docs-sa-assoc/AWS_Certified_Solutions_Architect_Associate_Feb_2018_%20Exam_Guide_v1.5.2.pdf).

<!--more-->

## Preparation
Its worth to mention that prior the preparation to this exam I had a little hands on experience with AWS and almost no theoretical knowledge. So I approached the preparation course as an AWS noob.

> **Q: Do I need to pay for AWS services if I want to pass this exam?**  
> **A:** no, you can pass it without having a real hands on, for instance by reading the AWS Study Guide alone. Though, the Free Tier offering by AWS will make the costs for AWS practice really close to $0. Without laying your hands on basic configuration stuff it could be challenging to pass the exam.

### Main course
Since I have an active [Linux Academy](https://linuxacademy.com/) subscription I took theirs [certification prep course](https://linuxacademy.com/amazon-web-services/training/course/name/aws-certified-solutions-architect-associate) which I found rather complete and well composed. Its the 20hrs length course with interactive quizzes and the real Hands On Labs. Labs are a great way to gain practice by having the access to AWS Console provided by the Linux Academy.

> ![pic](https://gitlab.com/rdodin/netdevops.me/uploads/46cf4e24404023a8a254b014d10b37ce/image.png)
> <center><small>Each section will test you on the outlined concepts. Most of them have real Labs</small></center>

Quizzes really help you to check that the material you've just listened to was actually absorbed by your memory. I went through all the videos on 1.5x speed and cleared all quizzes rather easily.  
At the very end of the course you can simulate the real exam by answering 60 questions in 80 minutes time frame. While the questions I had during the exam were harder, this simulation can help you to feel the real exam atmosphere.

While Hands On Labs are super useful to get the practical knowledge about the AWS Console and the configuration of the various services, I did not complete them all for the sake of time. But in general, I would highly suggest to clear Hands On Labs, most of the training providers offer them.

Linux Academy also has an assessment service called [Cloud Assessments](https://www.cloudassessments.com/). I completed the offered set of practice tasks and loved the gamification part they embedded. Solving the real practical tasks within the AWS Console can help you if you had no previous AWS management activities.

> ![img](https://pbs.twimg.com/media/DcB2qEAWsAEM9bX.jpg)
> <center><small>Cloud Assessments challenge you to solve different practice tasks for each major AWS service</center></small>

#### Main course alternatives 
Of course, Linux Academy is not the only service who made these AWS CSA prep courses, the most popular one I saw on the Internet was the [A Cloud Guru](https://acloud.guru/) course. Their students praise this course rather highly, so you can take that one as well. Check out the pricing and the course offerings to pick up the right provider for you.

### Additional resources
I hate to break it, but my experience showed that the course alone won't make you pass the exam easily. And not because the courses are not good enough, they are good, but they do not cover all the aspects or do not explain all the details of some service, which you might encounter during the exam.

#### Whitepapers
As a recommended supplement many courses suggest to go over the [AWS Whitepapers](https://aws.amazon.com/certification/certified-solutions-architect-associate/) to get more knowledgeable on the various AWS concepts. I've peered into the two of the papers and left the rest untouched. While the whitepapers are good and useful, they are ~70 pages long and reading them takes quite some time.

But if time allows, you better read them, since they cover a lot of the concepts you will be tested against. I hadn't that much time, so I went reading the Study Guide instead.

#### AWS CSA Official Study Guide
The [Study Guide](https://www.amazon.com/Certified-Solutions-Architect-Official-Study/dp/1119138558) offers the right amount of information to prepare you for the exam. I personally did not read the book, since I had a pretty good understanding of AWS services by finishing the LinuxAcademy course but if you don't want to pay for video course and Labs access, the Guide will do just fine.

I highly recommend to get your hands on this guide since it has a brilliant set of the Exam Essentials chapters and the straight-to-the-point quizzes after each chapter.

> ![aws_guide](https://gitlab.com/rdodin/netdevops.me/uploads/d97208aeaadca8c14a592850de72ce96/image.png)

All I did with this book was that I cleared all the quizzes after each chapter and read few "Exam essentials" chapters the day before the exam. And again, go over the quizzes, they are very good and if you'll cover them all, I would say you'd pass the exam with 80%+ score.

The quizzes in this Study Guide are better/harder than the ones I solved in the LinuxAcademy course, at the same time they are a good addition to the quizzes in the LinuxAcademy course. I must say that the quizzes had the most positive impact for me to clear the exam, since they helped me to discover my weak spots and focus on the topics where I made a lot of mistakes from the first attempt.

#### AWS FAQs
Now few posts on the Internet suggested to go over the FAQ section for each AWS service that is tested in AWS CSA exam. Thats a very good suggestion, since the FAQ section actually quite resembles the questions you might encounter during the exam. I breezed over two or three FAQs for [VPC](https://aws.amazon.com/vpc/faqs/), [RDS](https://aws.amazon.com/rds/faqs/) and SQS to see whats there; due to the time constraints I left other FAQs unread.

#### Catch up with a community
Its a wise move to explore how others mastered the exam and pick theirs preparation practices that might work for you as well. I found this two articles quite good and comprehensive, with lots of useful links and suggestions:

* [My AWS Solution Architect Associate exam experience](https://www.viktorious.nl/2018/01/10/my-aws-solution-architect-associate-exam-experience/) by Viktorious
* [Guide to Passing all 3 AWS Associate-level Certification Exams](https://medium.com/@annamcabee/guide-to-passing-all-3-aws-associate-level-certifications-73516bcef6e1) by Anna McAbee
* [AWS CSA discussion board on A Cloud Guru](https://acloud.guru/forums/aws-certified-solutions-architect-associate/)

### Analyze the weak spots
As I said, quizzed helped me to discover my weak spots. So I watched over some videos again and read few more topics, then I went over the quizzes again to make sure that I understood the problem well enough.

## Taking the exam
### What topics should I pay attention to most?
As I mentioned in the beginning, the actual questions I encountered during the exam were not easy-peasy. While, of course, I had a lot of basic questions that tested my ability to identify the key application area for the various AWS services, there were questions that required practical experience or detailed knowledge on the topic.

My point here, is that you will a fair share of questions that you could easily prepare to by reading the "Exam Essentials" topics of the above mentioned Study Guide, but will it be enough to safely pass the exam? Hard to tell.

Exam blueprint states that you will be tested for the following topics:

> Topic Level Scoring: <small>(with my marks)</small>  
> 1.0  Designing highly available, cost-efficient, fault-tolerant, scalable systems: 79%  
> 2.0  Implementation/Deployment: 100%  
> 3.0  Data Security: 77%  
> 4.0  Troubleshooting: 80%

No doubts, the most popular services will be tested the most:

- EC2
- S3
- RDS
- DynamoDB
- AutoScaling
- VPC

At the same time I was caught off guard by hitting quite a few questions dedicated to detailed knowledge of the following services:

- API Gateway
- ECS
- Lambda
- CloudFormation

My advice would be to pay a bit more attention to these topics, since they seem to appear frequently in the current versions of the CSA exam. And when I say "detailed knowledge", this means that questions were testing some configuration steps or your ability to identify the details about some service. 

Below I mention a few AWS concepts across various services that I did not master and was tested against, you better make sure to get familiar with these topics, since they are not normally stressed enough in the various prep courses.

**IAM**  
I had a false sense of simplicity when read IAM chapters. It seemed like everything is obvious with IAM. But then I got a question about the [AWS STS](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html) service and I was unprepared. Check this one out, don't be like me. So questions like temporary access are possible, and you need to know something about it.

If you are not coming from Systems Administration background you might shiver when you see AD/LDAP abbreviations in the question (I do). With this said, check that you know how AD policies can be integrated with AWS IAM.

Its very important to understand the huge importance of IAM Roles, I got the impression that I've been tested on this more than once. A tricky question was how can you let users from one AWS account access resources in another AWS account?

**EC2 Auto Scaling**  
Elasticity and High Availability are the corner stones of a modern cloud-based application, therefore you will face lots of Auto Scaling questions. Most of them are basic, but the interesting one happened to appear to me.

How does AS terminate the instance? In what order? Does it pick up a VM to terminate randomly or does it take into account active connections to the instance or maybe number of instances in the AZ?  
This is all about [Default Termination Policy](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-instance-termination.html) and my bad I did not pay attention to that specific angle of the EC2 Auto Scaling.

**S3**  
Normally S3 should come easy, aspects like Life-cycle policies and default data replication across AZs in a selected region must be emphasized by every course material. But ensure that you know what is S3 Cross-Region replication and why it might be needed.

Don't fool yourself that S3 Encryption questions will avoid you. Be ready to answer few questions on that.

**EBS**  
Do note, even though EBS in general might appear to you as an easy topic, AWS CSA tests you hard on EBS data encryption and protection. Spend few more hours on learning encryption options for EBS and the snapshots handling.

**Databases**  
Yes, fair share of DB related questions, mostly about RDS and DynamoDB. Be prepared to answer the multi AZ deployment questions. And do keep in mind that AWS RDS does not let you to access the underlying Operating System.

**VPC**  
Networks is my background, therefore VPC never got me much trouble. But for an _Average Joe_ it would be nice to ensure that topics like NAT Gateway and VPN/Direct Connect are not the strangers.

VPC endpoints concept is also something you need to know, as this might not stick in your memory from the first read.

**ECS**  
I believe that ECS related questions appeared in the AWS CSA exam not that long ago, moreover, the course materials (if they were not updated recently) probably will not emphasize enough on that topic, but do expect to see some questions on ECS as well.

The question that made me guess was something like the following: Can EC2 instances launched as the Ubuntu Linux servers be used as the [Container Instances](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/container_instance_AMIs.html) for the ECS?

**Cloudfront**  
The CDN concepts is easy to understand, but details might be not articulated well in the courses. For instance, you should know rather well, what services can leverage the CloudFront distribution, i.e. what are the backend services that CloudFront can provide CDN services for?

Also make sure that you understand what is CloudFront distribution and [how to configure](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.html#GettingStartedCreateDistribution) it. Specifically focus on Cache behaviors and [Path Patterns](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web-values-specify.html#DownloadDistValuesPathPattern). Note that the order of rules in the Path Patterns is crucial to the CloudFront, the `*` pattern should go after the more specific patterns!

**API Gateway**  
To see >1 question on that topic (and Lambda) was totally unexpected. I was under the impression that API GW will be tested on the very surface, but do expect some funny questions like [the CORS problem](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html#how-to-cors-console) and the API Gateway 

**Lambda**  
As with API Gateways, you will most probably see some Lambda questions thanks to the ever emerging Serverless concept. With Labmda its crucial to now about its scalability. Say you have a Lambda function provisioned to do some task with 150Mb of memory provisioned. If they ask you would you need to increase the memory per-function to handle the increased demand for that Lambda, the proper answer would be **No**, since AWS will scale this Lambda accordingly.

**Miscellaneous**  
My least favorite part is some corner services like AWS EMR, Kinesis, Redshift, etc.

For Kinesis you need to know the difference between the Kinesis Firehorse and Kinesis Streams.

For Redshift you need to have just a basic understanding about the sevice itself and when to choose it over RDS.

Generic security and compliance questions are easy, Shared Responsibility model is all you need to know I think. Even if you fail few of these questions, it won't matter much.

Do know how the role of `user-data` when provisioning EC2 instances and understand that it could be used for launching/passing scripts.

AWS KMS was also on the list with some shady question I couldn't even recall. CloudHSM was not there, but it might be in your exam...


### Passing score for AWS CSA exam
AWS does not disclose what is the passing score, I hit 81% and passed, but seems like the threshold varies quite significantly, check [this topic](https://acloud.guru/forums/aws-certified-sysops-administrator-associate/discussion/-K8gweqRXEr5zmCHPQ9P/passing-score-for-aws-certifications) for various reports of a pass/fail marks. Some passed with 60%, others failed with 70%...

### Watch out, time could be pressing
Apparently, 80 minutes for 55 questions could be a problem. I had 20 minutes left when I finished the last question, but I saw lots of comments, when others failed to finish in time. Some questions have lengthy explanation, so you loose time by reading it once/twice, then you could loose some more time on ruling out the right options. 

So my suggestion would be to skip the questions you can't answer in 1.5-2 mins interval. You can come back to skipped questions when you will deal with the rest of them.

Good luck with your exam!

![cert](https://gitlab.com/rdodin/netdevops.me/uploads/f0669ec7dd096f6b9c4e2a9b1d0894f8/image.png)

> Post comments [are here](https://gitlab.com/rdodin/netdevops.me/issues/7).
