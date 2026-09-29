# Prototype review hub

Stakeholders open this page to try a prototype:

**https://manselldesign.github.io/prototype-hub/**

Each prototype is its own public repository under [manselldesign](https://github.com/manselldesign). GitHub Pages serves the `index.html` at the root of that repository. The shareable link is always:

`https://manselldesign.github.io/<repo-name>/`

This repository is only the list. Do not put a new prototype’s files in here. Publish the prototype as its own repo, then add one line item to this page.

## Publish the next prototype

You need a GitHub personal access token that can create a public repository, push files, and turn on GitHub Pages. In the terminal, that token must be available as `GH_TOKEN` (or as `GITHUB_TOKEN`). Do not paste the token into a file, and do not commit it.

From a clone of this hub:

```bash
git clone https://github.com/manselldesign/prototype-hub.git
cd prototype-hub
export GH_TOKEN="your personal access token"
./tools/publish-prototype.sh /path/to/the/prototype-folder repo-name
```

Example, if the prototype folder on your computer is `~/Desktop/search-drawer` and the new repo should be named `search-drawer`:

```bash
./tools/publish-prototype.sh ~/Desktop/search-drawer search-drawer
```

The folder must contain `index.html` in its top level. Images and other files can sit beside that file. The command creates the public repo `manselldesign/repo-name`, pushes the `main` branch, turns on Pages from `main` at `/`, and prints the shareable link.

If a repository with that name already has files, the command stops and does not replace them.

The command does not edit this hub. After it prints the link, add the prototype to the list (step 4).

## Do it by hand

Use these four steps when you are not using the command above.

### 1. Create a new public repo under manselldesign

Go to [github.com/new](https://github.com/new) while signed in as **manselldesign**.

- Repository name: a short name with hyphens, such as `search-drawer`
- Visibility: **Public** (a private repo will not give stakeholders a working Pages link on this account)
- Leave “Add a README” unchecked so the repo starts empty

### 2. Put the prototype `index.html` at the repo root

The file stakeholders open must be named `index.html` and must sit at the top of the repository, not inside a folder. CSS, images, and scripts can sit next to it.

On GitHub, open the empty repo and use **Add file → Upload files**. Upload `index.html` and any files that sit beside it. Commit the upload to the `main` branch.

### 3. Enable Pages from `main` at `/`

In that prototype repo, open **Settings → Pages**.

- Source: **Deploy from a branch**
- Branch: **main**
- Folder: **/ (root)**

Save. The shareable link is:

`https://manselldesign.github.io/<repo-name>/`

The first build can take a minute. Refresh until the page loads.

### 4. Add one entry to the hub

Edit **`index.html`** in this repo ([manselldesign/prototype-hub](https://github.com/manselldesign/prototype-hub/blob/main/index.html)).

Find the list whose id is `prototype-list`. Copy one existing `<li>` block (there is also a commented example at the top of that list). Paste the copy at the top of the list and change three things:

- the heading (the name reviewers will see)
- the one-line description
- the link, which must be `https://manselldesign.github.io/<repo-name>/`

Commit that change to `main`. This hub’s own Pages site updates from that branch. The new prototype shows up on https://manselldesign.github.io/prototype-hub/ after the hub finishes building, usually within a minute.

## What reviewers see

The hub lists the name of each prototype, one line about what it is, and the live Pages link. When the list has no items, the page says nothing is listed yet and that new prototypes appear after they are published.
