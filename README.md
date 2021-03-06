## stypi-sync: Synchronize Stypi documents to local storage.

stypi-sync makes it easy to synchronize <a href="http://www.stypi.com">Stypi</a>
documents to local storage so you can edit code collaboratively and run it locally.
Right now it's very much alpha software -- certainly don't use it for anything you
don't have backed up or can't afford to lose changes to. If you want to improve
it, please contribute! And if you fork, please maintain the user-agent format
so the folks at Stypi can block it if anything goes amok.

### Quick start:

`python /path/to/stypi-sync/stypi-sync.py`

(or use an <a href="http://en.wikipedia.org/wiki/Alias_(command)">alias</a>! In your ~/.bashrc: `alias stypi-sync="python /path/stypi-sync.py"`)

This reads stypi-sync.json in your working directory to configure itself. That has a format like this:

`{"files":{"sandbox.html": "http://www.stypi.com/someid","code.js": "http://www.stypi.com/anotherone"}}`

Press enter to synchronize, kill with CTRL-C.

Note that stypi-sync is one-way only! It synchronizes from Stypi to your local storage. (It's assumed that you'll edit using Stypi right now.)

That's about it!

### To Stypi:

<a href="http://thumbs.reddit.com/t5_2sge2.png?v=42c4df73d1c4ad6037eaacd920ffe32e">Shut up and take my money!</a>

If this is killing your servers, I am sorry! I tried to make it friendly.
You can do any of the following things to block it:

 * Block its user agent (starts with "stypi-sync")

 * Break any of the fragile bits (they're even labelled!)
