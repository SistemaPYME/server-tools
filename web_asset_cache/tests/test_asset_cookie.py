from odoo.tests import HttpCase, tagged

BUNDLE = "web.assets_web_print"


@tagged("post_install", "-at_install")
class TestAssetCookie(HttpCase):
    def _bundle_url(self):
        bundle = self.env["ir.qweb"]._get_asset_bundle(BUNDLE, css=True, js=False)
        bundle.css()
        return bundle.get_link("css")

    def test_bundle_without_cookie(self):
        response = self.url_open(self._bundle_url())

        self.assertEqual(response.status_code, 200)
        self.assertIn("immutable", response.headers.get("Cache-Control", ""))
        self.assertNotIn("Set-Cookie", response.headers)

    def test_bundle_keeps_the_session_of_a_user(self):
        session = self.authenticate("admin", "admin")
        response = self.url_open(self._bundle_url())

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Set-Cookie", response.headers)
        # The user is still signed in afterwards.
        info = self.make_jsonrpc_request("/web/session/get_session_info")
        self.assertEqual(info["uid"], session.uid)

    def test_other_routes_still_set_the_cookie(self):
        response = self.url_open("/web/login")

        self.assertIn("session_id", response.headers.get("Set-Cookie", ""))
