#!/usr/bin/env python3
"""Loopback TCP forwarder: 127.0.0.1:<listen> -> <target_host>:<target_port>.
Lets the coordinator's SSH tunnel reach the owned Jenkins as http://localhost:8080 (same URL as the README).
Usage: forward.py 8080 host.docker.internal 18480"""
import asyncio, sys

LISTEN, THOST, TPORT = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])

async def pipe(r, w):
    try:
        while data := await r.read(65536):
            w.write(data)
            await w.drain()
    except (ConnectionError, asyncio.CancelledError):
        pass
    finally:
        w.close()

async def handle(cr, cw):
    try:
        tr, tw = await asyncio.open_connection(THOST, TPORT)
    except OSError:
        cw.close()
        return
    await asyncio.gather(pipe(cr, tw), pipe(tr, cw))

async def main():
    srv = await asyncio.start_server(handle, '127.0.0.1', LISTEN)
    async with srv:
        await srv.serve_forever()

asyncio.run(main())
