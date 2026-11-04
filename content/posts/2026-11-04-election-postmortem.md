---
layout: post
title: How did the election model perform?
date: 2026-11-04
description: A postmortem analysis.
---

The midterms aren't even 24 hours old yet, and results are still coming in.
If you read my blog post from [yesterday](https://www.ifyoucankeepit.org/p/we-may-not-know-the-midterm-results) you know that it's very likely some of these races will take many days to call, perhaps even several weeks.
Take [NC-03](https://www.nytimes.com/interactive/2026/11/03/us/elections/results-north-carolina-us-house-3.html), for example. The margin (at the time of this writing) is about 230 votes, out of about 238,000 total votes cast.
In races this close, it's not uncommon for there to be recounts, litigation, and other legal processes that can drag out an official call.

But the overall picture - a big blue wave - was clear from early yesterday evening.
The biggest question I hear people asking today isn't "what should Democrats focus on with their new majority?", or even "why did the Republican coalition collapse?". 
No, what I'm hearing over and over again is: "how accurate was Christian's election model??". 
So let's take a quick look.

My model, as of last night, gave the Democrats a 95% chance of control of the House, and a 71% chance to win the Senate. It predicted 28 governorships would be won by Democrats. 
Directionally, it was pretty close! Democrats indeed took the House and Senate, and appear to be on track to win 29 governorships.

But let's break it down a little bit more. We'll start with the House.
Although many races remain to be called, the prediction markets (again, at the time of this writing) are estimating a mean of 262 seats for the Democrats.
My model gave a 15% chance of at least 262 Democratic seats. Not too bad.

There are plenty of races where the model was off. That, I think, is to be expected, given the sparse polling in most of these races.
The House is big enough that I'm okay with ignoring the idiosyncracies in any given race, and blindly looking at the total number of seats instead.

In the Senate, Mississippi and Alaska remain to be called, although Democrats seem to hold the edge at the moment in both. Let's count them as Democratic wins for purposes of this evaluation.
Those two states would bring the Democratic tally to 56 seats. The model gave a 9% chance of at least 56 Democratic seats. 9% is sort of low, but not statistically significant. 
Directionally, however, the model missed on Kansas, South Carolina, Iowa, and (presumably) Mississippi, all of which it predicted a Republican victory for, and all of which went for a Democrat. 

Interestingly, this wasn't a case of simply underestimating the size of the blue wave. If that were the case, you'd expect a state like Nebraska at 79% chance of Republican victory (and which was indeed won by a Republican) to have flipped before Mississippi at 94% (and which ultimately seems to have been won by a Democrat).
Instead, the biggest problem was probably the lack of polls: none in Nebraska, and only a handful in Mississippi. The model was therefore heavily reliant on Cook ratings, which are somewhat uncertain.

Now, governorships. The biggest misses seem to have been Vermont, which the model gave a 78% chance of victory to the Democrat (and was ultimately won by a Republican), and Texas and Kansas, both of which were predicted to go Republican (with around an 80% chance) but went for a Democrat instead. 

So, a 2012-style "Nate Silver predicts every state correctly" victory lap is not in order. 
The next time around, I may have to do more to account for demographic patterns that can hold clues across states, dig more into the crosstabs on polls, or even look at extra data sources like fundraising numbers to get a better handle on races that have sparse polling. 
We'll revisit this in 2028. 