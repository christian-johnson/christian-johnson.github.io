---
layout: post
title: Updated Borsuk-Ulam App
date: 2026-01-03
description: Making a more user-friendly Borsuk-Ulam web app.
---

My previous [blog post]() showing how to detect Borsuk-Ulam points in real time worked, but I'm the first to admit that its UI was a bit lacking.
The animation is cumbersome, not super performant, and a bit basic-looking.
That's because I am not much of a web app developer - I've never written much (if any) JavaScript.
So I built the whole app in Python, with an Altair interactive chart.
Functional, yes.
But not user-friendly.

Enter AI.
In the process of playing around with Google's AI Studio, I found it to be quite capable of writing React code, which naturally led to the prospect of improving the Borsuk-Ulam app experience.
So I asked it to build a performant and modern-looking app with the same Python backend code.

Suffice it to say that this did not work out of the box.
Indeed, it took quite a bit of handholding to get something acceptable.
But the end result is certainly better than something I could have written myself.
Here's a screenshot:

![Screenshot of improved Borsuk-Ulam detector](/img/borsuk-ulam-screenshot_signed.png "Much nicer looking compared to before. And it's mobile-friendly too!")

The updated app now lives in its own [standalone repo](https://github.com/christian-johnson/borsuk-ulam), and can be visited on its own page [here](https://christian-johnson.github.io/borsuk-ulam).
Enjoy!
