![Power in the Hands of the Creators](https://github.com/ryanvilbrandt/comic_git/raw/docs/docs/img/comic_git_small.png)

# Building your website locally

```bash
git config submodule.comic_git_engine.ignore all
```

# TODO for v1.0 launch

* Get updated comic images from Caytlin for the showcase
* Update comic_git_showcase
* Update comic_git to what the website should look like for a new user
  * Update navigation icons to not use Tamberlane's icons
  * Add preview_image.png for the social media preview
* Write instructions for how to update from comic_git v0.3 to comic_git v1.0

## Update instructions notes

* Add `.nojekyll` file to the root of the repo to allow files starting with underscores to be served.

## Pre-launch steps

* Run Version update action to "1.0.0" in comic_git_engine
* Tag branch "1.0.0" as "v1"
* Update the Engine Version in the main comic_git to "1.0"
* Update the action call in the main comic_git to use "v1"

## Post-launch steps

* Update comicgit.com to point to comic_git_showcase

# Post 1.0 TODO

* Webring functionality