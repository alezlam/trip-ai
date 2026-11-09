import {serve} from '@hono/node-server';
import {serveStatic} from '@hono/node-server/serve-static';
import {Hono} from 'hono';

const app = new Hono();

app.get('/api/health', (c) => c.json({ok: true}));

// In dev, Vite serves the frontend and proxies /api here.
// In production, this one process serves both.
if (process.env.NODE_ENV === 'production') {
  app.use('/*', serveStatic({root: './dist'}));
  app.get('*', serveStatic({path: './dist/index.html'})); // SPA fallback
}

const port = Number(process.env.PORT ?? 3001);
serve({fetch: app.fetch, port}, () => {
  console.log(`server listening on http://localhost:${port}`);
});
