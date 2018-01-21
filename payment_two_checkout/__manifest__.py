# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Website 2Checkout Payment Acquirer",
  "summary"              :  "Integrate 2Checkout payment gateway with ODOO for accepting payments from customers.",
  "category"             :  "Website/Payment Acquirer",
  "version"              :  "1.1",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Prakash Kumar",
  "website"              :  "https://store.webkul.com/Odoo/Ecommerce-Website/Odoo-Website-2Checkout-Payment-Acquirer.html",
  "description"          :  """https://webkul.com/blog/odoo-website-2checkout-payment-acquirer
    Website 2Checkout Payment Acquirer
  """,
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=payment_two_checkout&version=10.0&custom_url=/shop/payment",
  "depends"              :  [
                             'payment',
                             'website_sale',
                            ],
  "data"                 :  [
                             'views/payment_2Checkout.xml',
                             'views/template.xml',
                             'data/2Checkout.xml',
                             'views/payment_acquirer.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  59.0,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}
