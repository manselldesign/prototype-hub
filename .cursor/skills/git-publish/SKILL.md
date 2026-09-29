---
name: git-publish
description: >-
  Publish an HTML prototype from the current Cursor project to
  github.com/manselldesign, turn on GitHub Pages, add it to the prototype
  review hub, and return the shareable link. Use when the user invokes
  /git-publish or /GitPublish, or asks to publish a local prototype, get a
  shareable link, or turn on GitHub Pages for manselldesign.
---

# GitPublish

Publish the open HTML prototype to the GitHub account **manselldesign** and reply with the live link.

The shareable link is always:

`https://manselldesign.github.io/<repo-name>/`

Reviewers also see it on https://manselldesign.github.io/prototype-hub/ after it is added to that hub.

## What the user must have open

The prototype folder must be the current workspace, or a folder inside it that the user named. `index.html` must sit at the top of that folder. CSS, images, and scripts may sit beside it.

If `index.html` is not in the workspace, stop. Tell the user to open the prototype folder in Cursor and send `/git-publish` again. Do not invent a prototype.

## What to collect

Use these defaults when the user already supplied them. Ask only for what is missing.

| Item | Rule |
| --- | --- |
| Folder | Directory that contains `index.html`. Prefer the workspace root. |
| Repo name | Short public repository name. Lowercase letters, numbers, and hyphens. Example: `search-drawer`. |
| Title | Name reviewers see on the hub. |
| One-line description | What the reviewer should look at. |

If the user typed `/git-publish search-drawer — Search opens in a drawer`, the repo name is `search-drawer`, the title is `Search drawer`, and the description is `Search opens in a drawer`.

## Publish

Run the script in this skill. Do not paste a token into a file, a command argument, or the chat. Do not commit a token.

```bash
bash .cursor/skills/git-publish/scripts/publish-prototype.sh "<folder>" "<repo-name>"
```

If this skill is installed in the home directory instead of the project, run:

```bash
bash ~/.cursor/skills/git-publish/scripts/publish-prototype.sh "<folder>" "<repo-name>"
```

The script creates the public repo `manselldesign/<repo-name>` when it does not already exist, pushes `main`, and turns on GitHub Pages from `main` at `/`.

If the repo already has files, the script stops and does not replace them. Tell the user the name is taken and ask for a new one. Do not force-push and do not delete the existing repo.

The script skips `.git`, `node_modules`, `.env` files, and key files. It adds `.nojekyll` so Pages serves the prototype as plain files.

## Add it to the review hub

After the script prints the link, add one entry at the top of the hub list:

```bash
bash .cursor/skills/git-publish/scripts/add-to-hub.sh "<repo-name>" "<title>" "<one-line description>"
```

Use the home-directory path when the skill is installed there. This edits only `index.html` in `manselldesign/prototype-hub`. It does not copy the prototype into the hub.

## Reply

Lead with the working link:

`https://manselldesign.github.io/<repo-name>/`

Say that the first visit can take about a minute while GitHub Pages builds, and that the same prototype is listed on https://manselldesign.github.io/prototype-hub/ after that hub finishes building.

If Pages did not turn on, still give the GitHub repository URL and say that the files are on `main`.

## Secrets

A token needs the `repo` scope so it can create a public repository, push, and enable Pages. The script reads the environment variable whose name is `GH` + `_TOKEN`, or `GITHUB` + `_TOKEN`. On Cloud Agents it also accepts the token from `CLOUD_AGENT_ALL_SECRET_NAMES`, from `gh auth token`, or from a swapped secret whose value is the text `GH` + `_TOKEN`.

If no token is available, stop and tell the user to save a Cursor secret named `GH` + `_TOKEN` whose value is their GitHub personal access token. Do not ask them to paste the token into the chat.
