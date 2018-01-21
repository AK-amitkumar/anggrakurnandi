# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################

import logging
_logger = logging.getLogger(__name__)
from odoo import http, _
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteSale(WebsiteSale):

    def _get_mandatory_billing_fields(self):
        return super(WebsiteSale, self)._get_mandatory_billing_fields()+['zip']
    def _get_mandatory_shipping_fields(self):
        return super(WebsiteSale, self)._get_mandatory_shipping_fields()+['zip']

    def wk_check_transaction(self):
        cr, uid, context = request.cr, request.uid, request.context
        transaction_obj = request.registry.get('payment.transaction')
        order = request.website.sale_get_order()
        if order and order.payment_tx_id:
            tx = order.payment_tx_id
            tx_id = tx.id
            if tx.sale_order_id.id != order.id or tx.state in ['error', 'cancel']:
                tx_id = False
            request.session['sale_transaction_id'] = tx_id
        else:
            request.session['sale_transaction_id'] = False
        return True

    @http.route(['/shop/payment'], csrf_token=False,type='http', auth="public", website=True)
    def payment(self, **post):
        self.wk_check_transaction()
        res = super(WebsiteSale, self).payment(**post)
        return res


class Wk2CheckoutController(http.Controller):
    _callback_url = '/payment/2checkout/feedback'

    @http.route(
        [_callback_url],
        auth="public", type='http', website=True)
    def wk_2checkout_form_feedback(self, **post):

        vals = {}
        transaction_obj = request.env['payment.transaction']
        transaction_id = transaction_obj.sudo().search(
            [('reference', '=', post.get('reference', ''))], limit=1)
        acquirer_id = transaction_id.acquirer_id
        if not acquirer_id:
            domain = [
                ('provider','=','two_checkout'),
                ('website_published','=',True),
            ]
            acquirer_id = request.env['payment.acquirer'].search(domain,limit=1)
        custom_error_msg = acquirer_id and acquirer_id.error_msg
        try:
            return request.env['payment.transaction'].sudo().twoCheckout_make_charges(post)
        except Exception as err:
            _logger.error("#WKDEBUG5 %r----%r"%(err, post))
            vals.update(
                {'error_msg': _(custom_error_msg or 'Something wrong happened , Please try again')})
            return request.render("payment_two_checkout.payment_2Checkout_error", vals)
