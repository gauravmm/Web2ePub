# Web2ePub
Converts articles/posts/entries from online sources into an ePub file. Websites are supported by a plugin architecture.

```
usage: web2epub.py [-h] [-o OUTPUT] [-s STYLE] [-c COVER] [--no-cover]
                   [--no-cache] [--no-overwrite]
                   url

Converts articles/posts/entries from online sources into an ePub file.

positional arguments:
  url                   A URL to start from. Must end with a forward slash (/)
                        if there is no path.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --out OUTPUT
                        The directory or filename to write to. epub
                        automatically appended if necessary. The target
                        directory must exist.
  -s STYLE, --style STYLE
                        The output style to use.
  -c COVER, --cover COVER
                        The cover generator to use, if the parser does not
                        find it.
  --no-cover            Do not generate a cover page if one does not already
                        exist.
  --no-cache            Force a cache miss and redownload the source material
                        on this request.
  --no-overwrite        Skip if the destination file exists.

```

## Websites

Currently, plugins are available for:
 - [What If](https://what-if.xkcd.com)
 - [FanFiction.net](https://fanfiction.net/)

I am taking requests for other websites, and will generally accept pull requests.

## Plugins

You can write new plugins to support additional websites, device-specific output, and cover page styles.

For details on how to write plugins, consult existing plugins in the `plugins/` directory and see the templates in `plugins.py`.

