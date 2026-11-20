from odoo.tests import TransactionCase, tagged

from ..models.web_asset_cache import BUNDLES_PARAM, CRON_XMLID

BUNDLE = "web.assets_web_print"


@tagged("post_install", "-at_install")
class TestWarmBundles(TransactionCase):
    def _attachments(self, bundle):
        return self.env["ir.attachment"].search(
            [("url", "=", bundle.get_link("css")), ("res_model", "=", "ir.ui.view")]
        )

    def test_missing_bundle_is_built(self):
        self.env["ir.config_parameter"].sudo().set_param(BUNDLES_PARAM, BUNDLE)
        bundle = self.env["ir.qweb"]._get_asset_bundle(BUNDLE, css=True, js=False)
        self._attachments(bundle).unlink()
        self.assertFalse(self._attachments(bundle))

        self.env["web.asset.cache"]._warm_bundles()

        self.assertEqual(len(self._attachments(bundle)), 1)

    def test_built_bundle_is_kept(self):
        self.env["ir.config_parameter"].sudo().set_param(BUNDLES_PARAM, BUNDLE)
        bundle = self.env["ir.qweb"]._get_asset_bundle(BUNDLE, css=True, js=False)
        attachment = bundle.css()

        self.env["web.asset.cache"]._warm_bundles()

        self.assertEqual(self._attachments(bundle), attachment)

    def test_unknown_bundle_does_not_stop_the_others(self):
        self.env["ir.config_parameter"].sudo().set_param(
            BUNDLES_PARAM, f"no_such.bundle, {BUNDLE}"
        )
        bundle = self.env["ir.qweb"]._get_asset_bundle(BUNDLE, css=True, js=False)
        self._attachments(bundle).unlink()

        self.env["web.asset.cache"]._warm_bundles()

        self.assertTrue(self._attachments(bundle))

    def test_bundle_names_default(self):
        self.env["ir.config_parameter"].sudo().set_param(BUNDLES_PARAM, "")
        self.assertIn("web.assets_web", self.env["web.asset.cache"]._get_bundle_names())

    def test_registry_load_triggers_the_cron(self):
        cron = self.env.ref(CRON_XMLID)
        triggers = self.env["ir.cron.trigger"].search([("cron_id", "=", cron.id)])

        self.env["web.asset.cache"]._register_hook()

        new = self.env["ir.cron.trigger"].search([("cron_id", "=", cron.id)]) - triggers
        self.assertEqual(len(new), 1)
