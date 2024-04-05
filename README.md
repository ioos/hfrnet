# ioos-documentation-jekyll-skeleton

A template/skeleton repository that can be used as a starting point to create a new IOOS GitHub Documentation Site for deployment to https://ioos.github.io/.

### Getting Started

See online documentation for working with this repository at: https://ioos.github.io/ioos-documentation-jekyll-skeleton/howto.html 

_Delete the 'ioos-documentation-jekyll-skeleton' heading above, delete this comment and the remaining text above, modify the reamaining README content below to be relevant to your documentation site, and make sure to change the Jekyll site configuration files accoridng to the instructions in the HOWTO/documentation. Once your site content looks ready to go, it can be pushed to the [IOOS GitHub Organization](https://github.com/ioos) to be deployed_

# IOOS Documentation Site: ___________

**Site URL:** https://ioos.github.io/your-documentation-repo-name



### Deploying site locally
Requirements:
* Ruby
* bundle
* Jekyll

Clone this repository:
```commandline
git clone https://github.com/ioos/ioos-documentation-jekyll-skeleton.git
```
Rename the resulting `ioos-documentation-jekyll-skeleton` directory to a name of your choice, and follow further [Getting Started](https://ioos.github.io/ioos-documentation-jekyll-skeleton/howto.html#getting-started) section in the HOWTO documentation.

To build the site, in your local renamed repo directory, run:
```commandline
bundle exec jekyll serve --config _config.yml --watch --verbose --incremental
```
This will deploy a website at: http://127.0.0.1:4000/ioos-documentation-jekyll-skeleton/.

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
And review at http://127.0.0.1:4000/ioos-documentation-jekyll-skeleton/

More settings changes, including renaming the site URL to match your new repository name (replacing 'ioos-documentation-jekyll-skeleton', should be made by editing the `_config.yml` and `_config_dev.yml` files in the repository root. See the [Edit Your Site Content](https://ioos.github.io/ioos-documentation-jekyll-skeleton/howto.html#step-2-edit-your-documentation-site-content) section of the the HOWTO.