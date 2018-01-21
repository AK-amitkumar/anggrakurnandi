# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################
import logging
_logger = logging.getLogger(__name__)

from odoo.addons.payment_two_checkout.libs import twocheckout
import werkzeug

from odoo import api, fields, models,_
from odoo import SUPERUSER_ID
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_two_checkout.controllers.main import Wk2CheckoutController

from odoo.http import request
_logger = logging.getLogger(__name__)


class AcquirerTwoCheckout(models.Model):

    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('two_checkout',  '2Checkout')])
    two_checkout_merchant_id = fields.Char(
        'Merchant ID ', required_if_provider='two_checkout', groups='base.group_user')
    two_checkout_public_key = fields.Char(
        'Public Key', required_if_provider='two_checkout', groups='base.group_user')
    two_checkout_private_key = fields.Char(
        'Private Key', required_if_provider='two_checkout', groups='base.group_user')


    @api.multi
    def two_checkout_get_form_action_url(self):
        """ Provide Post Url For 2Checkout Payment Form ."""
        self.ensure_one()
        return Wk2CheckoutController._callback_url


class TxTwoCheckout(models.Model):

    _inherit = 'payment.transaction'
    two_checkout_txnid = fields.Char('Transaction ID')

    @api.model
    def twoCheckout_make_charges(self, post):
        assert (post.get('twoCheckoutToken') !=
                None), _("Token Not Found  Please try Once Again. ")
        response = {}
        reference =  post.get('reference')
        tx_id =self.search([('reference', '=', reference)], limit=1)
        payment_acquirer_obj =tx_id.acquirer_id
        twocheckout.Api.auth_credentials({
            'private_key': payment_acquirer_obj.two_checkout_private_key,
            'seller_id': payment_acquirer_obj.two_checkout_merchant_id,
            'mode': payment_acquirer_obj.environment == 'prod'  and  'production'  or 'sandbox'
        })
        recipient = tx_id.partner_id
        args = {
            'merchantOrderId': str(reference),
            'token': str(post["twoCheckoutToken"]),
            'currency': str(post['currency']),
            # 'total': post['amount'],
            'billingAddr': {
                'name': str(recipient.name),
                'addrLine1': str(recipient.street),
                'city': str(recipient.city),
                'state': str(recipient.state_id and recipient.state_id.code or recipient.email),
                'zipCode': str(recipient.zip),
                'country': str(recipient.country_id.code),
                'email': str(recipient.email or recipient.notify_email),
                'phoneNumber': str(recipient.mobile or recipient.email)
            }
        }
        lineItems =[{
            "name": "Items %s"%reference,
            "price":  post['amount'],
            "type": "product", "quantity": "1"
        }]
        args.update({'lineItems':lineItems})
        response = twocheckout.Charge.authorize(args)
        response.update({'reference': reference})
        response.update({'transaction_id': reference})
        res = self.form_feedback(response, 'two_checkout')
        return werkzeug.utils.redirect(post.get('return_url', '/shop/payment/validate'))

    @api.model
    def _two_checkout_form_get_tx_from_data(self, data):
        reference = data.get('reference')
        if not reference:
            error_msg = _('Two Checkout: received data with missing reference (%s) or payment has not been captured ' % (
                reference))
            _logger.error("%s  %s"%(error_msg,data))
            raise ValidationError(error_msg)
        tx_ids = self.search([('reference', '=', reference)])
        if not tx_ids or len(tx_ids) > 1:
            message = tx_ids and 'Multiple order found'or 'No order found'
            error_msg = _('Two Checkout: Received data for reference %s .%s.' % (
                reference, message))
            _logger.error("%s  %s"%(error_msg,data))
            raise ValidationError(error_msg)
        return tx_ids[0]

    @api.multi
    def _two_checkout_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        return invalid_parameters

    @api.model
    def _two_checkout_form_validate(self,  data):
        vals = dict(
                date_validate = fields.datetime.now(),
                acquirer_reference = data.get('transactionId'),
                two_checkout_txnid = data.get('transactionId'),
                state = data.get('responseCode') == 'APPROVED'  and   'done' or 'error' ,
                state_message =   data.get('responseMsg',_('2Checkout: feedback error'))
            )
        return self.write(vals)
