from odoo import models
from odoo.http import request

ASSET_PATH_PREFIX = "/web/assets/"


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _pre_dispatch(cls, rule, args):
        # A bundle is the same for every visitor, but Odoo saves the session and sends
        # Set-Cookie with it, and a CDN does not keep a response that sets a cookie.
        # This covers /web/assets/<unique>/<file> and the website one with its id.
        if request.httprequest.path.startswith(ASSET_PATH_PREFIX):
            request.session.can_save = False
        return super()._pre_dispatch(rule, args)
