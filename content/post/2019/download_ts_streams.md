---
title: How to download an M3U/M3U8 playlist (stream) without a special software
date: 2019-06-20T10:00:07+00:00
author: Roman Dodin
# layout: post
draft: false
comment_id: m3u8 download
keys:
  - m3u8
  - video
  - youtube-dl
tags:
  - m3u8
  - video
  - youtube-dl
---

I love the tech conferences that share the recordings of the sessions without hiding behind the registration or a pay wall. Luckily the trend to share the knowledge with a community openly is growing, yet you still can find a nice talk hidden behind the above mentioned walls. 

Sometimes an easy registration is all it takes, but then, how do you watch it offline? For example, I do love to catch up with with the recent trends and experiences while being on a plane, meaning that I just cant afford to be hooked up to the Internet.

If a talk is published on the YouTube, you are good to go and download it with any web service that pops up in the google search by the term "Youtube download". But what do we do when the video is hosted somewhere in the CDN and is served as a dynamic playlist of `*.ts` files?

Here I share with you an easy way to download the videos from an [m3u/m3u8]([m3u8](https://en.wikipedia.org/wiki/M3U)) playlist.

<!--more-->

The dynamic playlist format - M3U/M3U8 - is a way to tell the browser how to download the pieces of the video that will comprise the whole recording. So the download process is actually as easy as:

1. Get the m3u8 link
2. Download every file from that playlist and glue them into a single video.

# Getting the playlist URL
Now the first part is easy, you go to the page where a vide player is rendered and search for the `m3u8` file using the developers tools console of your browser.

![m3u8](https://gitlab.com/rdodin/pics/-/wikis/uploads/d93e36091a2753714bdb6e56ba796a70/image.png)

Make sure to get the master playlist request url and copy it in your clipboard.

## Video quality
In the master playlist body you can see the different versions of the playlists, typically they differ with the quality settings. Consider the following m3u8 file contents:

```bash
#EXTM3U
#EXT-X-VERSION:4
#EXT-X-STREAM-INF:PROGRAM-ID=0,BANDWIDTH=180400,CODECS="mp4a.40.2,avc1.4d001e",RESOLUTION=720x294,AUDIO="audio-0",CLOSED-CAPTIONS=NONE
https://manifest.prod.boltdns.net/...
#EXT-X-STREAM-INF:PROGRAM-ID=0,BANDWIDTH=335500,CODECS="mp4a.40.2,avc1.4d001f",RESOLUTION=1200x490,AUDIO="audio-1",CLOSED-CAPTIONS=NONE
https://manifest.prod.boltdns.net/...
```

The first cropped link is for the playlist with 720x294 resolution, whereas the second one is a HQ version with "1200x490" stream. If you see that for some reason you are downloading the low quality stream, extract the HQ stream URL and use it instead of the master playlist URL.

# Downloading the files
## with VLC
The title of this post says "... with no special software", yet we will use the [VLC](https://www.videolan.org/vlc/) player here which I deliberately categorize as a software that everyone can get on every platform, so its not a special software.

What you need to do next is to choose **File -> Open Network** dialog and paste the URL of the m3u8 playlist from the prev. step. Now you can either play it in the VLC right away, or check the **Stream Output** checkbox and click **Settings**.

![m3u](https://gitlab.com/rdodin/pics/-/wikis/uploads/a7e2a5ccdb760fcb543914f7c244183b/image.png)

This will open a new dialog where you can choose:

* the path to a resulting video file
* the video container format
* and, optionally, the audio/video codecs if you want to do transcoding

![settings](https://gitlab.com/rdodin/pics/-/wikis/uploads/84ac91ad725e848045ea53ad5d818c0c/image.png)

Click **Ok** and the files will start to download and encode in your resulting video container by the path you specified. This is not a particularly fast process, so just wait till the progress bar reaches its end and enjoy the video!

## with youtube-dl
The VLC-way is good for a one-time quick download, but if you have a list of playlists you want to download, then [youtube-dl](https://github.com/ytdl-org/youtube-dl/blob/master/README.md#readme) python tool is just unmatched. Judging by the name, the tool was developed for youtube downloads originally but outgrew it quickly enough to be a swiss knife for online video downloads.

You can install it as a python package or as a pre-compiled binary, so the installation is really a breeze and won't take long. Additionally, the tool brings an endless amount of features:

* automatically detect playlist URL by crawling the HTML page (no need to manually look for m3u8 URL)
* cli interface to scriptify bulk downloads
* extensive encoding support via ffmpeg and aconv
* filtering and sorting for videos in the playlists (if the playlist has more than one vide, i.e. Youtube playlist)
* and **many** more.

For example, to download a video that you would normally watch at http://example.com/vid/test a single CLI command is all it takes:

```bash
# name the output file test.<container_format>
youtube-dl -o 'test.%(ext)s' --merge-output-format mkv http://example.com/vid/test
```
and the rest is handled by the marvelous youtube-dl:

```
[download] Downloading playlist: Search query
[Search] Downloading search JSON page 1
[Search] Downloading search JSON page 2
[Search] Downloading search JSON page 3
[Search] playlist Search query: Downloading 75 videos
[download] Downloading video 1 of 75
[author:new] 6047188571001: Downloading webpage
[author:new] 6047188571001: Downloading JSON metadata
[author:new] 6047188571001: Downloading m3u8 information
[author:new] 6047188571001: Downloading m3u8 information
[author:new] 6047188571001: Downloading MPD manifest
[author:new] 6047188571001: Downloading MPD manifest
[hlsnative] Downloading m3u8 manifest
[hlsnative] Total fragments: 245
[download] Destination: test.fhls-430-1.mp4
[download]  69.0% of ~81.31MiB at 577.84KiB/s ETA 01:57
```

Sometimes, though, you can't just specify the URL of a page where the player is normally loaded in your browser, due to the cookies presented in your browser and who knows what black magic this frontenders invented while we were not watching.  
Then you still need to manually fetch the m3u8 link and feed it to the `youtube-dl`. The rest stays the same, the tool will handle the download/encoding process in the most effective and pleasant way.

Note, you also might need to download the `ffmpeg` for youtube-dl to merge the different streams in a single container. Anyway, `youtube-dl` will tell you if its the case for you.

> If you like what I'm doing here and in a mood for sending a token of appreciation, you can leave a comment, or use one of the buttons below  
> <iframe src="https://github.com/sponsors/hellt/button" title="Sponsor hellt" height="35" width="107" style="border: 0;"></iframe>
<a href="https://www.buymeacoffee.com/ntdvps" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/lato-orange.png" alt="Buy Me A Coffee" style="height: 51px !important;width: 217px !important;" ></a>