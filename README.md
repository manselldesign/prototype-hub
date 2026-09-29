# Prototype review hub

Stakeholders open this page to try a prototype:

**https://manselldesign.github.io/prototype-hub/**

New prototypes live **in this repository** as a folder plus a card on the homepage. Example: Prototype-Mega-Hover is `mega-hover/index.html`, listed on the homepage, live at:

`https://manselldesign.github.io/prototype-hub/mega-hover/#/`

Do **not** create a new GitHub repo for each prototype unless someone explicitly asks for a standalone repo.

## Publish from Cursor

Open the prototype (it needs `index.html` at the top of that folder). In Agent chat:

```text
/git-publish Prototype-Mega-Hover — desktop mega menu and mobile header CTAs
```

Stay in that chat. If `gh` is already signed in as **manselldesign**, the agent publishes from here. If not, use **GitHub device login** (`gh auth login`) in the same chat — do not start with “open a new Cloud Agent.”

The agent copies `index.html` into `prototype-hub/<slug>/`, updates this homepage, pushes `main`, and replies with:

`https://manselldesign.github.io/prototype-hub/<slug>/#/`

The slug comes from the name (`Prototype-Mega-Hover` → `mega-hover`). The first visit can take about a minute while GitHub Pages builds.

The skill is `.cursor/skills/git-publish/`. Cursor’s skill name is lowercase, so the command is `/git-publish`. To use it from every prototype folder, copy that directory to `~/.cursor/skills/git-publish` once, then turn on Sync Skills for Cloud Agents.

## Publish from a clone of this hub

```bash
./tools/publish-to-hub.sh /path/to/the-prototype-folder slug "Title reviewers see" "One line about what to look at."
```

That command needs `gh` signed in as **manselldesign**. It does not create a new repository.

## Do it by hand

1. Copy the prototype `index.html` into a new folder in this repo, such as `my-slug/index.html`.
2. Add a list item at the top of `#prototype-list` in this repo’s `index.html`. The link must be `https://manselldesign.github.io/prototype-hub/my-slug/#/`.
3. Commit and push **main**.

## Protected standalone repos

Do not overwrite `manselldesign/rivet-nav-prototype` (A), `rivet-nav-zoo-header` (B), `rivet-nav-zoo-source` (C), or the unrelated `manselldesign/mega-hover`. Those stay as they are. Iterations of Prototype-Mega-Hover go in **this** repo under `mega-hover/`.
