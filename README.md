## stypi-sync: Synchronize Stypi documents to local storage.

### Quick start:

python /path/to/stypi-sync/stypi-sync.py

This reads stypi-sync.json in your working directory as configuration. It has the format:
    `{
    `    "files":{
    `        "sandbox.html": "http://www.stypi.com/someid",
    `        "code.js": "http://www.stypi.com/anotherone"
    `    }
    `}

Press enter to synchronize, kill with CTRL-C.

### To Stypi:

<a href="http://thumbs.reddit.com/t5_2sge2.png?v=42c4df73d1c4ad6037eaacd920ffe32e">Shut up and take my money!</a>

If this is killing your servers, I am sorry! I tried to make it friendly.
You can do any of the following things to block it:

 * Block its user agent (starts with "stypi-sync")

 * Break any of the fragile bits (they're even labelled!)
