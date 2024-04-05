# IOOS Documentation Site: HFRNet

**Site URL:** https://ioos.github.io/hfrnet



### Deploying site locally
Requirements:
* Ruby
* bundle
* Jekyll

Clone this repository:
```commandline
git clone https://github.com/ioos/hfrnet.git
```
Follow [Getting Started](https://ioos.github.io/ioos-documentation-jekyll-skeleton/howto.html#getting-started) section in the HOWTO documentation.

To build the site, in your local renamed repo directory, run:
```commandline
bundle exec jekyll serve --config _config.yml --watch --verbose --incremental
```
This will deploy a website at: http://127.0.0.1:4000/hfrnet/.

Further instructions for modifying and configuring your site can be found in the  [Editing and configuring your documentation site](https://ioos.github.io/ioos-documentation-jekyll-skeleton/howto.html#editing-and-configuring-your-documentation-site) section of the HOWTO.

#### Editing site content

Make edits to the appropriate markdown files in `_docs/`. 

If changing headers and menus, stop the running server by entering `ctrl-c` in the terminal. Then run:
```commandline
bundle exec jekyll clean
```
Then build the site again.
```commandline
bundle exec jekyll serve --config _config.yml --watch --verbose --incremental
```
And review at http://127.0.0.1:4000/hfrnet/

More settings changes, including renaming the site URL to match your new repository name (replacing 'ioos-documentation-jekyll-skeleton', should be made by editing the `_config.yml` and `_config_dev.yml` files in the repository root. See the [Edit Your Site Content](https://ioos.github.io/ioos-documentation-jekyll-skeleton/howto.html#step-2-edit-your-documentation-site-content) section of the the HOWTO.
