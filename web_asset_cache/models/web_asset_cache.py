import logging
import time

from odoo import api, models

_logger = logging.getLogger(__name__)

BUNDLES_PARAM = "web_asset_cache.bundles"
DEFAULT_BUNDLES = "web.assets_web,web.assets_web_print,web.assets_frontend"
CRON_XMLID = "web_asset_cache.ir_cron_warm_bundles"


class WebAssetCache(models.AbstractModel):
    _name = "web.asset.cache"
    _description = "Asset bundle warm-up"

    def _register_hook(self):
        # Runs once each time Odoo loads the registry, that is after every deploy:
        # the bundles get a new hash and are built by the cron, not by the first
        # visitor. The cron is triggered and not run here, so the start is not slowed.
        res = super()._register_hook()
        cron = self.env.ref(CRON_XMLID, raise_if_not_found=False)
        if cron and cron.active:
            cron.sudo()._trigger()
        return res

    @api.model
    def _get_bundle_names(self):
        value = (
            self.env["ir.config_parameter"].sudo().get_param(BUNDLES_PARAM)
            or DEFAULT_BUNDLES
        )
        return [name.strip() for name in value.split(",") if name.strip()]

    @api.model
    def _warm_bundles(self):
        """Build the minified files of the configured bundles that are missing.

        A bundle already built for its current version is left as it is.
        """
        rtl_variants = [False]
        if self.env["res.lang"].search_count(
            [("active", "=", True), ("direction", "=", "rtl")], limit=1
        ):
            rtl_variants.append(True)
        qweb = self.env["ir.qweb"].sudo()
        for name in self._get_bundle_names():
            start = time.monotonic()
            try:
                # Each bundle on its own: a failure leaves the others built.
                with self.env.cr.savepoint():
                    bundle = qweb._get_asset_bundle(name, css=False, js=True)
                    if bundle.javascripts or bundle.templates:
                        bundle.js()
                    for rtl in rtl_variants:
                        bundle = qweb._get_asset_bundle(
                            name, css=True, js=False, rtl=rtl
                        )
                        if bundle.stylesheets:
                            bundle.css()
            except Exception:
                _logger.exception("Could not build the asset bundle %s", name)
                continue
            _logger.info(
                "Asset bundle %s ready in %.1f s", name, time.monotonic() - start
            )
