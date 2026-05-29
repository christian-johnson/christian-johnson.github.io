---
layout: post
title: Sakharov, a vibe-coded text editor with notebook support
date: 2026-05-29
description: A project to build a personal text editor with all my favorite features.
---

In a [previous post](https://christianjohnson.xyz/posts/2025-04-15-helix-ipython/), I did a survey of options for literate programming options, and landed on Helix as a good solution, due to:
- Speed (Helix is written in Rust and is quite snappy)
- Healthy supply of built-in features
- Simple configuration

However, it doesn't have any support for Jupyter notebooks, so it requires a little bit of finagling to get a good setup, and each setup is terminal-dependent. 

Then I read [this](https://sockpuppet.org/blog/2026/05/12/emacsification/) blog post on the "Emacsification of Software" - basically, about how LLMs are enabling personal app development.
So in that spirit, I decided to try building out a brand-new text editor that had all the features I wanted, i.e. a Helix-style experience with Jupyter support.

A few days of prompting Claude Code later, and I managed to get something usable, which I'm calling `sakharov` after the great Soviet physicist and dissident. 
It features:
- Cross-cell LSP support in notebooks
- Code & cell folding
- Async code execution
- Image support (in terminals that support it)

It's certainly not at feature parity with any major text editor on the market, but I still think it's pretty neat. 
You can find a link to it on my [Projects](https://christianjohnson.xyz/projects) page. 

