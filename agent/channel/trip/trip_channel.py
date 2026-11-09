"""trip-ai public channel: the process's only listener.

Serves the Trip AI API under /api/* and the built React frontend from dist/.
Replaces CowAgent's web console, which trip-ai removed.

Config (config.json):
  trip_host  bind address, default 127.0.0.1. Set 0.0.0.0 in production.
  trip_port  default 8080.
"""

import asyncio
import os

from aiohttp import web

from channel.channel import Channel
from common.log import logger
from common.singleton import singleton

# agent/channel/trip/ -> repo root -> dist/
DIST_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "dist"))


@singleton
class TripChannel(Channel):
    channel_type = "trip"

    def startup(self):
        # Runs on its own thread (ChannelManager), so it owns its own event loop.
        asyncio.run(self._serve())

    async def _serve(self):
        app = web.Application()
        app.router.add_get("/api/health", self._health)
        app.router.add_get("/{tail:.*}", self._frontend)

        runner = web.AppRunner(app)
        await runner.setup()
        host = self.cfg("trip_host", "127.0.0.1")
        port = int(self.cfg("trip_port", 8080))
        try:
            await web.TCPSite(runner, host, port).start()
        except OSError as e:
            logger.error(f"[TripChannel] cannot bind {host}:{port}: {e}")
            self.report_startup_error(str(e))
            return
        logger.info(f"[TripChannel] listening on http://{host}:{port}")
        self.report_startup_success()
        await asyncio.Event().wait()  # serve until the process exits

    async def _health(self, request):
        return web.json_response({"ok": True})

    async def _frontend(self, request):
        """Serve a built asset, or index.html for client-side routes."""
        index = os.path.join(DIST_DIR, "index.html")
        if not os.path.isfile(index):
            return web.Response(status=404, text="frontend not built: run `npm run build`")
        tail = request.match_info["tail"]
        if tail.startswith("api/"):
            return web.json_response({"error": "not found"}, status=404)
        path = os.path.realpath(os.path.join(DIST_DIR, tail))
        # Path containment: never serve a file outside dist/.
        if path.startswith(DIST_DIR + os.sep) and os.path.isfile(path):
            return web.FileResponse(path)
        return web.FileResponse(index)
