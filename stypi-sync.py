#!/usr/bin/env python

"""
stypi-sync -- Synchronize Stypi documents to local storage.

Improvements and notes:
    - Requires Python 2.6+
    - This code is not ready for production! You could lose your work if
      something goes terribly wrong.
    - stypi-sync isn't differential; it requests the most recent revision each
      time it's run. It would be more effecient to reverse-engineer their
      websocket protocol in full and save whenever it got a difference like
      their proper web client.

Copyright (C) 2011 by Sam Birch (sbirch.net)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import sys, urllib2, random, time, websocket, threading, json, os

USER_AGENT = 'stypi-sync variant: original/0.1'
#this is arbitrary & I have no idea if it makes a difference; this is more or
#less what I've seen in practice though.
USER_NUMBER = random.randint(20000, 25000)

def parse_stypi_url(url):
    return url.rsplit('/',1)[1]

def make_request(url, id):
    headers = {
        'Host': 'node.stypi.com:8000',
        'Connection': 'keep-alive',
        'Referer': 'http://www.stypi.com/%s' % id,
        'Origin': 'http://www.stypi.com',
        'User-Agent': USER_AGENT,
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'
    }
    request = urllib2.Request(url, None, headers)
    return request

class StypiStream:
    def __init__(self, id, user_id, callback, debug=False):
        """
        Do not make the mistake of thinking I have figured out their websocket
        protocol: I have not. But! I have figured out just enough to get the
        head.
        """
        self.id = id
        self.user_id = user_id
        self.send_counter = 1
        self.has_sent_handshake = False
        self.callback = callback
        self.debug = debug
    def send_data(self, ws, data):
        msg = b'5:%d+::%s' % (self.send_counter, data)
        self.send_counter += 1
        if self.debug:
            print 'Sent: %r\n' % msg
        ws.send(msg)
    def parse_message(self, data):
        #this is fragile.
        return json.loads(data[6:])
    def send_handshake(self, ws):
        self.send_data(ws, '{"name":"message","args":[{"type":"handshake","docId":"%s","userId":%d,"subscriptions":["text","cursor","chat"]}]}' % (self.id, self.user_id))
    def on_error(self, ws, error):
        if self.debug:
            print 'Websocket error (ignoring): %r' % error
    def on_open(self, ws):
        if self.debug:
            print '### Websocket Open ###'
    def on_close(self, ws):
        if self.debug:
            print '### Websocket Closed ###'
    def on_message(self, ws, message):
        if self.debug:
            print 'Message: %r\n' % message
        if not self.has_sent_handshake:
            self.send_handshake(ws)
            self.has_sent_handshake = True
        else:
            self.callback(self.id, self.parse_message(message)[0][u'headtext'])
            ws.close()

def get_session_id(id):
    request = make_request('http://node.stypi.com:8000/socket.io/1/?t=%d&jsonp=0' % (time.time() * 1000), id)
    f = urllib2.urlopen(request)
    data = f.read()
    f.close()
    #this is also fragile.
    return int(data[9:-3].split(':',1)[0])

def get_most_recent_revision(id, sessionid, callback):
    stream = StypiStream(id, USER_NUMBER, callback)
    
    ws = websocket.WebSocketApp("ws://node.stypi.com:8000/socket.io/1/websocket/%d" % sessionid,
        on_message = stream.on_message,
        on_error = stream.on_error,
        on_close = stream.on_close)
    ws.on_open = stream.on_open
    
    threading.Thread(target=ws.run_forever).start()

def synchronize(id_map):
    recv_map = {}
    for id in id_map:
        recv_map[id] = None
    
    def add_to_queue(id, text):
        recv_map[id] = text
    
    for id in id_map:
        session = get_session_id(id)
        get_most_recent_revision(id, session, add_to_queue)
        time.sleep(0.1)
    
    print 'Downloading %d files' % len(id_map)
    
    last_left = -1
    while True:
        left = sum([1 for x in recv_map if recv_map[x] == None])
        if left != last_left:
            print '%d remaining to be downloaded' % left
            last_left = left
        if left == 0:
            break
        else:
            time.sleep(0.1)
    
    for id in id_map:
        directory = os.path.dirname(id_map[id])
        if not os.path.isdir(directory) and not os.path.exists(directory):
            os.makedirs(directory)
        elif os.path.exists(directory) and not os.path.isdir(directory):
            print '%s exists, but is not a directory. Skipping.' % directory
            continue
        file = open(id_map[id], 'wb')
        file.write(recv_map[id])
        file.close()
    
    print 'Synchronization complete!'

def read_configuration():
    try:
        config = open('./stypi-sync.json', 'rb')
        data = json.load(config)
        config.close()
    except Exception as e:
        print e
        return None, False
    
    def fixfile(file):
        return os.path.join(os.getcwd(), file)
    
    if data.has_key(u'files'):
        data = data['files']
        syncset = {}
        
        for file in data:
            syncset[parse_stypi_url(data[file])] = fixfile(file)
        
        return syncset, True
    return None, False

if __name__ == '__main__':
    while True:
        raw_input('Press enter to sync...')
        
        syncset, valid = read_configuration()
        if not valid:
            print 'Configuration not valid!'
            continue
        
        synchronize(syncset)
        
        print ''