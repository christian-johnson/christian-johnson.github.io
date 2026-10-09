---
layout: post
title: An open source election forecast model
date: 2026-10-10
description: Can we have Nate Silver? No, we have Nate Silver at home.
---

I was as saddened as anyone to see ABC's neglect of, and eventual [erasure](https://www.natesilver.net/p/disney-erased-fivethirtyeight) of the data journalism site FiveThirtyEight.
For the last ten or fifteen years, they were one of my go-to sources for analysis and modeling of elections. 
Nate Silver, for all his various faults, almost single-handedly moved election forecasts into the mainstream, which is a pretty remarkable achievement.

I think a fair critique of his election model, however, is that it isn't open-source. 
We know it's [Stata](https://x.com/NateSilver538/status/1853674744953917839) code, but we don't know exactly how it works.
The most detailed documentation appears to be on Silver's [Substack](https://www.natesilver.net/p/model-methodology-2024), but it's not detailed enough to be reproducible. 
Obama-era Silver was somewhat more forthcoming with his metholodogy. [Here's](https://web.archive.org/web/20080719034906/http://www.fivethirtyeight.com/2008/04/pollster-ratings-v30.html) an early FiveThirtyEight post that explains in some detail their pollster ratings.

The reason for this, I gather, is that the model is his intellectual property, which is eminently reasonable.
After all, he's the [#2](https://substack.com/leaderboard/76739/rising) bestselling U.S. Politics Substack, and presumably a decent amount of those subscriptions exist, in large part, to see the outputs of his model (which is behind a paywall).
But the academic in me is a little miffed that the trend has been towards less transparency, not more.

Note: this is not the only open source election model out there. There are plenty of others, to be sure. [Here's](https://github.com/keithpotz/Election-Prediction) one on GitHub. 
[Here's](https://github.com/TheEconomist/us-potus-model) the Economist's 2020 presidential model.
That's what's nice about open source software, though - anyone can contribute to the ecosystem!
Even me, who has never published a forecast of any kind before (though, to be fair, I've modeled election data [previously](https://arxiv.org/abs/2110.03661)).

Fortunately, software is getting easier to write every day, thanks to AI & coding agents.
Since the election is coming up soon (24 days!) and I don't know what Nate's model says, I thought I'd build my own model and open-source it.
"How hard could it be, really?" I said to myself.

Answer: surprisingly easy!
AI is really good at writing web apps these days. My previous post from [October 2025](https://christianjohnson.xyz/posts/2025-10-01-rent-buy/), where I complained that AI coding had a long way to go, now looks pretty shortsighted, doesn't it?

[Here's](https://christianjohnson.xyz/election-forecast) the app. (I've also linked it on my Projects page.) [Here's](https://github.com/christian-johnson/election-forecast/) the source code. 
Yes - it's built with AI. Do with that information what you will.

There are caveats to be aware of.
I did specify pretty carefully the architecture of the model itself. 
In particular, I insisted the model combine its estimation of pollster house effects with fitting the poll results themselves (i.e., treating the house effects as a nuisance parameter to be modeled, not an input to the model).
But of course, modeling involves a series of many decisions, which can produce bias. This model, as a result, is biased towards the design of other similar models in the literature.

Perhaps that's why its outputs are similar to the other election forecasts out there (not to mention betting markets).
Or, perhaps the converging of forecast probabilities across modalities is just the correct reflection of all the public data available.
We'll find out in early November.