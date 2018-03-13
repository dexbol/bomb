Bomb (Boomjs builder)
=====================

A builder for web frond-end, optimize specially for boomjs.


Install Requirement
--------------------

*   Java Runtime Environment(JRE). Because of Bomb use google closure compiler
    and YUI compresser to compile files of css or javascript.

*   [option] Any subversion client with command-line tools, if you use SVN for
    your project. I advise you install it. The benefit of the case is that Bomb
    will update and commit automatically. If you using TortoiseSVN, it makes
    easy to get command tools, refer
    <http://stackoverflow.com/questions/1625406/using-tortoisesvn-via-the-command-line#answer-1625416)>.

TIPS: You should change the PATH system variable that make operation system
can locate java executale files and subversion comment-line tools. Read
[this](http://www.java.com/en/download/help/path.xml) for more information.


Install
--------

### Windows Installer(Deprecated, only for old version) ###

Download `setup.exe`. Run it, `Next` `Next` and `Next`. Congratulations!

### Use pip ###

    pip install bomb

### Install from source code ###

Download source code from here. Unpackage, run cmd.exe or bash, change the
current working directory to directory that contain `setup.py` and type:

    python setup.py install


Quickstart
-----------

1.  Make a package config file.

    Suppose you have a workspace directory in `C:\project`, and the directories
    tree looks like this:

        template/
        static/
            css/
                a.css
                b.css
            js/
                jquery.js
                a.js
                b.js
            cfile/
            store/
        ...

    You should make a package config file named `package.json` in 'static/', and
    copy this to your file.

        {
            "cfile": ["./cfile/"],
            "referrer":["../template/head.tpl"],
            "store": "./store"
        }

    Let's explain these key. `cfile` is a array that include config file
    directory(explain "config file" later). The value `./cfile/` means all config
    files in `C:\project\static\cfile\`. `referrer` is a template file such as
    php template or a html file that introduce javascript or css. `store` is a
    directory that contain files that compile config files to. The last, one case
    need to take care is that all path we mention above is relative to the directory
    of `package.json`, in this case it's `C:\project\static`.

    Now, the directories tree looks like this:

        template/
        static/
            package.json
            css/
                a.css
                b.css
            js/
                jquery.js
                a.js
                b.js
            cfile/
            store/
        ...    

2.  Make some config files.

    Suppose our project need one css file and one javascript file in production
    environment. And the css file includes all css files that in `static/css`, 
    the javascript file includes all javascript files in `static/js`. For this
    case we make two config files: one.css and one.js in `static/cfile/`.
    `one.css` looks like this:

        @import url('./css/a.css');
        @import url('./css/b.css');

    `one.js` looks like this:

        $import('./js/jquery.js');
        $import('./js/a.js');
        $import('./js/b.js');

    So, the directories tree looks like this:

        template/
        static/
            package.json
            css/
                a.css
                b.css
            js/
                jquery.js
                a.js
                b.js
            cfile/
                one.css
                one.js
            store/
        ...    

    There is **caveat**, all the path in config file is relative to the
    directory of package config file(in this case is `static/`), IS NOT relative
    to itself. 


3.  Make a template file.

    As eveyone knows, javascript and css must be included in a html file. Now,
    we make a html template file named `head.tpl` in `template/` to include css
    and javascript. Anthor template can include `head.tpl` in order to include
    javascript and css. It looks like this:

        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Bomb Test</title>
            {if $PRODUCTION_ENVIRONMENT}
                <link rel="stlyesheet" type="text/css" href="/static/store/one_0.css">
                <script src="/static/static/store/one_0.js"></script>
            {else}
                <link rel="stlyesheet" type="text/css" href="/static/css/a.css">
                <link rel="stlyesheet" type="text/css" href="/static/css/b.css">
                <script src="/static/static/store/js/jquery.js"></script>
                <script src="/static/static/store/js/a.js"></script>
                <script src="/static/static/store/js/b.js"></script>
            {/if}
        </head>
    
    Now, the directories tree looks like this:

        template/
            head.tpl
        static/
            package.json
            css/
                a.css
                b.css
            js/
                jquery.js
                a.js
                b.js
            cfile/
                one.css
                one.js
            store/
        ...    

That's all, all files that we need are exsit. Here we go. Use Bomb publish this
project.

If you install Bomb by Windows Installer, you can bring the context menu by
right click `package.js`, then click `Bomb`. In other way else you need run
cmd.exe or bash and type

    bomb package.json

You will see a list of config file even use what way you chose. Then type `all`
and `Enter`. Bomb will run and process course of actions e.g. compile config file,
modify template file and commit the change to server by SVN. All Done, The
directoies tree looks like this:

        template/
            head.tpl
        static/
            package.json
            css/
                a.css
                b.css
            js/
                jquery.js
                a.js
                b.js
            cfile/
                one.css
                one.js
            store/
                one_1.css
                one_1.js

`one_1.js` includes `jquery.js` `a.js` and `b.js`, and it compressed by Google
Closure Compiler. `one_1.css` is the same.

`head.tpl` is changed too. the path `/static/store/one_0.css` change to
`/static/store/one_1.css`. javascript file is the same.

And if this project use SVN, all change commited to server already. That's all.


More Feature
------------

If you use Google Pagespeed, you should know inlineing small CSS files can
enhance speed of page rendering. Bomb do this easily. Use the example above,
But we need change `head.tpl` to this:

    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Bomb Test</title>
        {if $PRODUCTION_ENVIRONMENT}
            <style>
            /*  _PLACEHOLDER_one.css START  */

            /*  _PLACEHOLDER_one.css END  */
            </style>
            <script src="/static/static/store/one_0.js"></script>
        {else}
            <link rel="stlyesheet" type="text/css" href="/static/css/a.css">
            <link rel="stlyesheet" type="text/css" href="/static/css/b.css">
            <script src="/static/static/store/js/jquery.js"></script>
            <script src="/static/static/store/js/a.js"></script>
            <script src="/static/static/store/js/b.js"></script>
        {/if}
    </head>

Run Bomb, the content of one.css will appear between the annotations.