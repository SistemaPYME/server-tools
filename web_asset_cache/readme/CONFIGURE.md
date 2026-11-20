The system parameter `web_asset_cache.bundles` lists the bundles to build, separated by
commas. By default: `web.assets_web,web.assets_web_print,web.assets_frontend`. The
right-to-left version of the CSS is built too when a right-to-left language is active.

Cloudflare caches `.js` and `.css` files by their extension as soon as the response has
no cookie: check that `cf-cache-status` says `HIT` on the second request of a bundle. If
it says `DYNAMIC` or `BYPASS`, add a Cache Rule for `/web/assets/*` that makes it
eligible for cache and respects the origin's `Cache-Control`.
