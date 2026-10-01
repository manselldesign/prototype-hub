---
name: git-publish
description: >-
  Publish an HTML prototype into manselldesign/prototype-hub as a folder plus
  homepage card, and return the GitHub Pages URL. Use when the user invokes
  /git-publish or /GitPublish, or asks to publish a local prototype or get a
  shareable review link. Default is the hub, not a new repository.
---

# GitPublish

Put the open prototype on **manselldesign/prototype-hub** and reply with:

`https://manselldesign.github.io/prototype-hub/<group>/<slug>/#/`

That is a **folder** in a group (`<group>/<slug>/index.html`) plus a card on the hub homepage and on that group’s page (`<group>/index.html`). Groups are `mega`, `header`, `sidebar`, `drill-down`, and `breadcrumbs`. Do **not** create a new GitHub repo unless the user clearly asks for a **standalone repo**.

Never push to, overwrite, or recreate these existing standalone repos: `rivet-nav-prototype` (Prototype A), `rivet-nav-zoo-header` (B), `rivet-nav-zoo-source` (C), or the unrelated `manselldesign/mega-hover`. Prototype-Mega-Hover lives at **`prototype-hub/mega/mega-hover/`**, not in `manselldesign/mega-hover`.

## Stay in this chat

1. Run `gh auth status`. If it is signed in as **manselldesign**, keep working in this chat.
2. If it is not signed in, do **GitHub device login here**: `gh auth login` (GitHub.com, HTTPS, login with a web browser). Wait for her to finish the device code. Then continue.
3. Do **not** tell her to start a new Cloud Agent as the first instruction.
4. Never paste a token into chat, a file, or a command the user can see. Never commit a token.

## What must be open

Need the prototype’s `index.html`. Prefer the folder she named. In this Vite hub that is often `prototypes/<slug>/index.html`. If there is no `index.html`, stop. Do not invent a prototype.

## Slug, title, description

Use what she already typed. Ask only for what is missing.

| Item | Rule |
| --- | --- |
| Folder | Directory that contains `index.html`. |
| Slug | From the prototype name: drop a leading `Prototype-`, lowercase, hyphens only. Example: `Prototype-Mega-Hover` → `mega-hover`. |
| Group | `mega` for `mega-*`, `header` for `header-*`, `sidebar` for `sidebar-*`, `breadcrumbs` for `breadcrumb*`, `drill-down` for `drill-*`. Pass it as the fifth argument when the slug does not say. |
| Title | Name on the hub card. |
| Description | One line about what a reviewer should look at. |

`/git-publish Prototype-Mega-Hover — desktop mega menu and mobile header CTAs` → slug `mega-hover`, title `Prototype-Mega-Hover`.

Refuse slugs `tools`, `index`, `.cursor`, `mega`, `header`, `sidebar`, `drill-down`, or `breadcrumbs`.

## Publish (this is the usual path)

```bash
bash .cursor/skills/git-publish/scripts/publish-to-hub.sh "<folder>" "<slug>" "<title>" "<description>" ["<group>"]
```

If the skill is only in the home directory:

```bash
bash ~/.cursor/skills/git-publish/scripts/publish-to-hub.sh "<folder>" "<slug>" "<title>" "<description>" ["<group>"]
```

The script copies `index.html` into `prototype-hub/<group>/<slug>/index.html`, adds or updates the card on the homepage and the group page, and pushes **main**. Updating the same slug is OK (that is how iterations work).

## Standalone repo (only if she asks)

Only if she explicitly wants a **new standalone repo**, run `scripts/publish-prototype.sh`, then stop if the name is protected (see above). The shareable link for that rare path is `https://manselldesign.github.io/<repo-name>/`.

## Reply

Lead with:

`https://manselldesign.github.io/prototype-hub/<group>/<slug>/#/`

Say the first visit can take about a minute while GitHub Pages builds, and that the same item is on https://manselldesign.github.io/prototype-hub/.
