---
layout: post
title: Will we have AI middle managers?
date: 2026-05-25
description: Some wild speculation about the future of agentic work.
---

The trends in agentic engineering are clear: more agents, more tokens, more ambitious projects.
I thought it would be interesting to speculate on what will happen if these trends continue.

Cursor's [experiment](https://cursor.com/blog/scaling-agents) with building a web browser from scratch used hundreds of agents (its ultimate failure notwithstanding).
One could imagine even more ambitious projects - building an operating system from scratch, writing entirely new programming languages that are better suited for LLMs, or building new LLMs entirely.
These projects might require thousands (or even tens of thousands!) of agents working in parallel.

But AI isn't magic - it's still subject to the same constraints that the rest of us are.
With, say, tens of thousands of agents working in parallel, the constraints that matter are the laws of combinatorics and economics.
Taken together, these imply that AI might need not only to mimic human writing, but human bureaucracies as well.

Let's start with combinatorics.
With a thousand agents, it is nigh impossible for each agent to keep track of what each other agent is up to. 
The context window for each agent is finite, and it will quickly become polluted trying to monitor other agents.
Therefore agents will have to be choosy about how many agentic relationships they maintain.
Just like company with 100 staff will naturally create different teams of, say, 5-10 people working on a specific project, an AI swarm would do well to create small teams as well.
Cursor discovered this in their experiment - their initial approach had a flat organizational structure and allowed agents to self-organize.
Only after introducing a three-tiered hierarchy (worker agents, planner agents, and judging agents) did they start to make some progress.

The other consideration is economics.
The number of dollars that can be spent on a given project is finite.
That means, on some level, a token budget will need to be drawn up: 20% of the budget allocated for feature X, 10% allocated for feature Y, etc.
Trade-offs will need to be made. 
How much of the budget should be allocated to testing? To security reviews? To performance improvements?
These aren't easy questions to answer, and AI agents will likely struggle to answer them well, just as human organizations do.

In Cursor's case, as a well-funded startup, they didn't have to worry too much about blowing the budget on any particular feature.
But other projects will.
Agents will have to decide whether it's worth it to keep spending money on a feature that is behind schedule, or to triage it for later.
They'll have to decide whether divisions of the swarm need to be laid off entirely (maybe that division's task was poorly formulated and needs to be rewritten), or whether to hire additional workers for that division instead.

And leadership agents will have to do it with incomplete information - they won't have full insight into what has been tried already, because to have full insight would mean to completely fill up their own context window.
So the leadership agents will have to make their decisions by consulting with other agents to get a summarized, incomplete picture of the situation.
Team leaders, for their part, will have to advocate for additional resources.
And so on.

As I see it, we will naturally end up with full-fledged AI bureaucracy, just as in a normal company.
Presumably AI bureaucracy will be lacking an HR department, but corporate reorganizations, cross-team collaboration initiatives, and performance reviews are all on the table.
At the top of it all is the CEO - maybe that's the human in charge of the project, maybe it's an AI agent (and the human acts as the board of directors, responsible for hiring/firing the CEO).

As with any bureaucracy, politics will be an emergent phenomenon. 
Fighting for additional resources and power will become an important part of the role of AI managers. 
What will be the appropriate political structure to manage thousands of agents?
Will it be an entirely top-down hierarchical organization?
Or will the best structure be something closer to a worker-owned cooperative, where all agents have a say in how the project is managed?
I have no idea - but it will be interesting to find out what is most effective. 