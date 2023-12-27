# Cluboeno

Cluboeno is a french blog about wines, spirits and other fun stuff

## Installation

It's a static web site made with Hugo (www.gohugo.io)

- Install Hugo
- Download sources
- Run Hugo

### Nearly finished

In order to see your site in action, run Hugo's built-in local server.
```
$ hugo server
```
Now enter [`localhost:1313`](http://localhost:1313) in the address bar of your browser.

## Hugo Theme : NederburgByLechaps

I use a personnal theme, this was ported from Hugo Nederburg (https://github.com/appernetic/hugo-nederburg-theme)
Features add/modified :

- french traduction
- drop G+ link (Seriously, who know Google Plus now?)
- about page have his own page (not the same as post page)
- avatar from static image and not gravatar link(Seriously, who use Gravatar?)
- more identation (Seriouly, who can read the original code ?)
- minors fixes

## Configuration

First, let's take a look at the **config.toml**. It will be useful to learn how to customize your site. Feel free to play around with the settings.

### More style customizations?

Create `css/custom.css` in your `<<base dir>>/static` folder and add all your custom styling.

### Comments

The optional comments system is powered by [Disqus](https://disqus.com). If you want to enable comments, create an account in Disqus and write down your shortname in the config file.
```toml
disqusShortname = "your-disqus-short-name"
```
You can disable the comments system by leaving the `disqusShortname` empty.

### Make the contact form working

Since this page will be static, you can use [formspree.io](//formspree.io/) as proxy to send the actual email. Each month, visitors can send you up to one thousand emails without incurring extra charges. Begin the setup by following the steps below:

1. Enter your email address under 'email' in the **config.toml**
2. Upload the generated site to your server
3. Send a dummy email yourself to confirm your account
4. Click the confirm link in the email from [formspree.io](//formspree.io/)
5. You're done. Happy mailing!

## Multiple Writers Features

In order to support multiple writers, an extra key, "writers" is added, in **config.toml**. The format looks like the following:
```
  [params.writers."LeChaps"]
    link = "myLink"
    email = "me@me_again.cmo"
    avatar = "/img/my-icone.jpg"
    bio = ["Seriously, you know it'great!"]
    facebook      = "full lechaps profile url in facebook"
    twitter       = "full profile url in twitter"
    linkedin      = "full profile url in linkedin"
    stackoverflow = "full profile url in stackoverflow"
    instagram     = "full profile url in instagram"
    github        = "full profile url in github"
    pinterest     = "full profile url in pinterest"
```
Now you must have an author in the config for the author bio section to be visible. If you have a writer and set it in the markdown file it will override the author in the config. See the exampleSite folder for a working solution.

## Tag management by Python scriptin

- tags-dictionnary.json : contains all the tags research by the script and managed by hugo
- tag-write.py : uses this script to create the tag line on md files lookinf for tags from dictionnary
- tag-extract.py : use this script to extract and count all the tag from md

## License

This port is released under the MIT License.

## Thanks

- [Steve Francia](https://github.com/spf13) for creating Hugo and the awesome community around the project.
- [goransv](https://github.com/appernetic) for creating this nice theme.
- [Joshua Paul Barnard](https://github.com/JoshuaPaulBarnard/) for creating the backbone of the interactive wine aroma wheel

## Sponsors

mmm, i don't have sponsors. But do i need them?

[lechaps](https://github.com/lechaps)
