import uwsgi
import time

def application(env, sr):

    ws_scheme = 'ws'
    if 'HTTPS' in env or env['wsgi.url_scheme'] == 'https':
        ws_scheme = 'wss'

    if env['PATH_INFO'] == '/':
        sr('200 OK', [('Content-Type','text/html')])
        output = """
    <!doctype html>
    <html>
      <head>
          <meta charset="utf-8">
          <script language="Javascript">
            var s = new WebSocket("%s://%s/foobar/");
            s.onopen = function() {
              console.log("connected !!!");
              s.send("hello");
            };
            s.onmessage = function(e) {
        var bb = document.getElementById('blackboard')
        var html = bb.innerHTML;
        bb.innerHTML = html + '<br/>' + e.data;
            };

        s.onerror = function(e) {
            console.log(e);
        }

    s.onclose = function(e) {
        console.log("connection closed");
    }

            function invia() {
              var value = document.getElementById('testo').value;
              s.send(value);
            }
          </script>
     </head>
    <body>
        <h1>WebSocket</h1>
        <input type="text" id="testo"/>
        <input type="button" value="invia" onClick="invia();"/>
    <div id="blackboard" style="width:640px;height:480px;background-color:black;color:white;border: solid 2px red;overflow:auto">
    </div>
    </body>
    </html>
        """ % (ws_scheme, env['HTTP_HOST'])
        return output.encode()
    elif env['PATH_INFO'] == '/favicon.ico':
        return ""
    elif env['PATH_INFO'] == '/foobar/':
        uwsgi.websocket_handshake(env['HTTP_SEC_WEBSOCKET_KEY'], env.get('HTTP_ORIGIN', ''))
        print("websockets...")
        msg_srv_fd = uwsgi.async_connect("127.0.0.1:8888")
        websocket_fd = uwsgi.connection_fd()
        while True:
            uwsgi.wait_fd_read(websocket_fd, 3)
            uwsgi.wait_fd_read(msg_srv_fd)
            uwsgi.suspend()
            fd = uwsgi.ready_fd()
            if fd > -1:
                if fd == websocket_fd:
                    msg = uwsgi.websocket_recv_nb()
                    print("got message over ws: {}".format(msg))
                    if msg:
                        uwsgi.send(msg_srv_fd, msg)
                elif fd == msg_srv_fd:
                    msg = uwsgi.recv(msg_srv_fd)
                    print("got message over msg_srv: {}".format(msg))
                    uwsgi.websocket_send("[%s] %s" % (time.time(), msg.decode()))
            else:
                # on timeout call websocket_recv_nb again to manage ping/pong
                msg = uwsgi.websocket_recv_nb()
                print("ws ping/pong")
                if msg:
                    print("got message over ws: {}".format(msg))
                    uwsgi.send(msg_srv_fd, msg)
