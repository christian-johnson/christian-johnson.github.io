---
layout: post
title: REPL-driven development in Helix
date: 2025-04-15
description: A workflow using IPython in Helix.
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
A notebook or REPL-based workflow solves this problem, because it keeps everything in memory.
Notebooks have their own challenges, of course, most importantly that the state can be hidden from the user (if you execute a cell and then delete it, your work isn't reproduceable).
But if you're careful, it can be a powerful way of doing analysis.

I've explored many of the options out there for tools that enable this kind of workflow.
The following is a (nonexhaustive) list of tools that I've experimented with, and my (highly subjective!) experience with each:

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

**Cons:** No real LSP support (despite many folks' attempts). Scrolling over large or numerous plots is buggy.

#### [Zed REPL](https://zed.dev/docs/repl)

**Pros:** Fast. Good LSP support.

**Cons:** Zed's business model nags you about signing in and using their collaboration features, and the devs are [unwilling](https://github.com/zed-industries/zed/issues/13218) to change that.

#### [Euporie](https://github.com/joouha/euporie)

**Pros:** Widget support. Full TUI Jupyter experience.

**Cons:** Doesn't integrate with your text editor of choice. LSP support is hit-or-miss.

#### NeoVim plugins ([vim-slime](https://github.com/jpalardy/vim-slime), [iron.nvim](https://github.com/Vigemus/iron.nvim), [magma](https://github.com/dccsillag/magma-nvim))

**Pros:** Runs via Neovim, which is a fully customizable TUI editor. Combining with [quarto](https://quarto.org/docs/tools/neovim.html) and [otter](https://github.com/jmbuhr/otter.nvim) gives some LSP support and can produce beautiful interactive outputs.

**Cons:** Many of the core features here can be reproduced in Helix without the use of plugins.

#### [Marimo](https://marimo.io/)

**Pros:** Nice UI (JS widgets work). Dependencies can be specified between blocks so that the notebook is perfectly reproduceable.

**Cons:** Not particularly customizable. Using your favorite text editor to write raw Python files is cumbersome - each block is delimited by an @app.cell decorator, and has to live within a function (to see what I mean, take a look at one of the [examples](https://github.com/marimo-team/marimo/blob/main/examples/markdown/details.py)).

#### [Helix](https://helix-editor.com) + IPython

**Pros:** Fast, customizable, full LSP support. Up and running with literally 2 lines of code.

**Cons:** No widget support. Plugins not available yet.

Previously, I used Emacs and Org-mode code blocks.
It works great (if you install the [emacs-jupyter](https://github.com/emacs-jupyter/jupyter) plugin), but I became increasingly frustrated by the lack of LSP support and a few other rough edges, like the poor image handling.
Plus, I like to change things up every now and again just for fun.

As you've already guessed from the title of this blog post, I have (for the time being) switched to using Helix.
Helix is a relatively young TUI text editor written in Rust that takes a "batteries-included" philosophy: my config is 42 lines long as of this writing (compared to my Emacs config, which was over 1000 lines).
And I'm able to reproduce a REPL-driven development with just the following snippet:

```toml
[keys.normal]
"S-i" = ":sh wezterm cli split-pane --horizontal --percent 40 --cwd $(pwd) -- sh -c 'uv run ipython' >/dev/null"
"S-s"= [":pipe-to wezterm cli send-text --pane-id $(wezterm cli list --format json | jq '.[] | select(.title | contains(\"IPython\"))| .pane_id' -r)",
":pipe-to wezterm cli send-text --no-paste --pane-id $(wezterm cli list --format json | jq '.[] | select(.title | contains(\"IPython\"))| .pane_id' -r) '\r'"]
```

This defines two keybindings:

When in Normal mode, `I` launches an IPython REPL in my WezTerm session on the right side of the screen.
And when in Visual mode, `S` sends the selection to the REPL and executes it.
That way, I can maintain a pure Python script on one side of my screen, using Helix's full LSP and editing capabilities, and still get the ability to iterate quickly on code snippets.

Here's a recording of what I mean:

{{< rawhtml >}} 

<figure>
  <video controls width="640">
    <source src="/video/helix_ipython.mp4" type="video/mp4">
  </video>
</figure>

{{< /rawhtml >}}

In the video, I first open up a new IPython instance with `I`.
This launches the window on the right. I navigate back to the Python file I'm editing, select some rows, and pass them to the REPL with `S`.
As a bonus, I even modified my .matplotlibrc file to default to matching my terminal's color scheme, purely for eye candy.
And, as you can see in the video, LSP functions like documentation lookup and autocomplete are unaffected.
