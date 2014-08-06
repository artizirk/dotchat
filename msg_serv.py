#!/usr/bin/env python3
import asyncio

class EchoServer(asyncio.Protocol):
    clients = {}
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('connection from {}'.format(peername))
        self.transport = transport
        self.clients[transport] = None

    def data_received(self, data):
        # print('data received: {}'.format(data.decode()))
        for transport in self.clients:
            if transport == self.transport:
                pass
                #continue
            transport.write(data)

    def connection_lost(self, exc):
        print("connection lost")
        self.transport.close()
        del self.clients[self.transport]

loop = asyncio.get_event_loop()
coro = loop.create_server(EchoServer, "127.0.0.1", 8888)
server = loop.run_until_complete(coro)
print('serving on {}'.format(server.sockets[0].getsockname()))

try:
    loop.run_forever()
except KeyboardInterrupt:
    print("exit")
finally:
    server.close()
    loop.close()
