---
layout: post
title: REPL-driven development in Helix
date: 2025-04-10
description: A workflow using IPython in Helix.
tags: programming
categories:
chart:
---

Like many data scientists, I'm a big fan of REPL-driven and notebook workflows because they allows me to quickly inspect data and iterate on ideas.
A typical problem might be: given some (large-ish) data set, build and fit a model, and then evaluate how well the model performs.
The steps, generally, are:
1. Import necessary libraries
2. Load the data into memory from disk or a database
3. Instantiate the model
4. Fit the model
5. Evaluate the model by computing metrics or making plots

It's wasteful to run these steps in sequence by putting all the code into a script, because the slowest steps (loading/cleaning the data, and fitting the model) don't need to be re-done every time I want to change the color of my histogram.
Therefore, we use REPLs. 

I've explored many of the options out there for tools that enable this kind of workflow.
None of them are perfect, but here's my experience with each option that I've tried, and my subjective pros/cons about each:

#### [VS Code notebooks](https://code.visualstudio.com/docs/datascience/jupyter-notebooks)

**Pros:** Most polished interface (JavaScript widgets, smooth scrolling). Customizable. Full LSP support. You should probably just use this.

**Cons:** Runs as an Electron app. Uses Microsoft's proprietary LSP. A fully integrated experience - your terminal, version control, file explorer are all the same program (this might not be a con to some folks, but I like to tinker with my individual components).

#### [Jupyter notebooks/JupyterLab](https://jupyter.org/)

**Pros:** Widgets work. Easy to share & export (GitHub supports displaying notebooks).

**Cons:** Dated UI. LSP support is not built-in. Editing cells with a text editor is highly cumbersome.

#### [Google Colab notebooks](https://colab.google.com)

**Pros:** Free (limited) compute available on GPUs/TPUs. Easy to share with collaborators.

**Cons:** Not particularly customizable. Your kernel can and will die if you step away for a while, because Google will reclaim those compute resources for itself.

#### [Org-mode notebooks (in Emacs)](https://orgmode.org/worg/org-contrib/babel/intro.html)

**Pros:** Highly adaptable with elisp scripts. Multi-language support in a single document (e.g., Python code blocks can seamlessly interface with Bash or elisp blocks). 

**Cons:** No real LSP support (despite many attempts). Scrolling over large or numerous plots is buggy.

#### [Zed REPL](https://zed.dev/docs/repl)

**Pros:** Fast. Good widget and LSP support.

**Cons:** Zed's business model nags you about signing in and using their collaboration features, and the devs are [unwilling](https://github.com/zed-industries/zed/issues/13218) to change that. 

#### NeoVim plugins (vim-slime, iron.nvim, magma, quarto)

**Pros:** Runs via Neovim, which is a fully customizable TUI editor. Some LSP support in the case of Magma, full LSP support in the case of iron.nvim and vim-slime. Quarto can produce beautiful interactive outputs.

**Cons:** Most of the core features here that I care about can be reproduced in Helix without the use of a plugin. Quarto docs can be produced from a `.qmd` file.

#### Marimo

**Pros:** Nice UI (JS widgets work). Dependencies can be specified between blocks so that the notebook is perfectly reproduceable.

**Cons:** Not particularly customizable. Using your favorite text editor to write raw Python files is cumbersome (each block is delimited by a @cell decorator). 

#### [Helix](https://helix-editor.com) + IPython

**Pros:** Fast, customizable, full LSP support. Up and running with literally 2 lines of code. 

**Cons:** No widget support. Plugins not available yet. 

Previously, I used Emacs and Org-mode code blocks.
It works great (if you install the [emacs-jupyter]() plugin), but I became increasingly frustrated by the lack of LSP support and a few other rough edges, like the poor image support.
Plus, I like to change things up every now and again just for fun.

As you've already guessed from the title of this blog post, I have (for now) switched to using Helix.
Helix is a relatively young TUI text editor written in Rust that has is much more "batteries-included" than Emacs.
My config is 42 lines long as of this writing (compared to my Emacs config, which was over 1000 lines).
And I'm able to reproduce a REPL-driven development with just the following snippet:

```{toml}
[keys.normal]
"S-i" = ":sh wezterm cli split-pane --horizontal --percent 40 --cwd $(pwd) -- sh -c 'uv run ipython' >/dev/null"
"S-s"= [":pipe-to wezterm cli send-text --pane-id $(wezterm cli list --format json | jq '.[] | select(.title | contains(\"IPython\"))| .pane_id' -r)",
":pipe-to wezterm cli send-text --no-paste --pane-id $(wezterm cli list --format json | jq '.[] | select(.title | contains(\"IPython\"))| .pane_id' -r) '\r'"]
```

Here's a recording of what I mean:
{% include video.liquid path="assets/video/tutorial_al_folio.mp4" class="img-fluid rounded z-depth-1" controls=true autoplay=false %}

In the video, I first open up a new IPython instance by typing "I" (for IPython).
This launches the window on the right. I navigate back to the Python file I'm editing, select some rows, and pass them to the REPL with "S" (for Send).
As a bonus, I even modified my .matplotlibrc file to default to matching my terminal's color scheme, purely for eye candy.
And, as you can see in the video, LSP functions like documentation lookup and autocomplete are unaffected.
