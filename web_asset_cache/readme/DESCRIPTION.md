Makes the asset bundles of Odoo (`/web/assets/...`) cacheable by a CDN such as
Cloudflare, and builds them again right after each deploy.

- Odoo saves the session on every request, also for a bundle, and answers with
  `Set-Cookie: session_id`. A CDN does not keep a response that sets a cookie, so every
  visitor reached the server for 1-2 MB of JavaScript. With this module a bundle is
  answered without saving the session and without a cookie. The bundle already carries
  `Cache-Control: public, max-age=31536000, immutable` and a hash in its URL.
- After a deploy the bundles get a new hash and Odoo built them on the first request,
  which took seconds for that visitor. Each time Odoo loads the registry, this module
  triggers a cron that builds the missing ones.
