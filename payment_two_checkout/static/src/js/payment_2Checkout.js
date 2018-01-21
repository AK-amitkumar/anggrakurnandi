odoo.define('payment_two_checkout.payment_two_checkout', function (require) {
      var ajax = require('web.ajax');

        $(document).ready(function(){
            var currentTime = new Date();
            $("#wk_2checkout_credit_card_expMonth").selectedIndex= Number(currentTime.getMonth());

            var year = currentTime.getFullYear();
            var wk_2checkout_year = $("#wk_2checkout_credit_card_expYear");
            for (var i = year+15; i >= year; i--) {
             wk_2checkout_year.prepend("<option value="+ i +">" + i + "</option>");
            }
            if ($('#submit_2checkout_payment').length>0){
              var environment=$('#submit_2checkout_payment').data('environment');
              var env = environment=='prod' ?  'production'  : 'sandbox'
              TCO.loadPubKey(env);
            }
            submit_2checkout_payment_odoo=function (token) {
                var $form =$('#payment_2checkout_form');
                     $('#wk_2checkout_myModal').modal('hide');
               var acquirer_id = $form.parents('div.oe_sale_acquirer_button').first().data('id');
                 ajax.jsonRpc('/shop/payment/transaction/' + acquirer_id, 'call', {}).then(function (data) {
                    if (typeof(data) != 'number'){
                        $form=$(data);
                    }
                    var $input=''
                    if (token){
                       $input = $('<input type=hidden name=twoCheckoutToken />').val(token.response.token.token);
                    }
                    $form.append($input);
                    $(document.body).append($form);
                    $form.submit();
                    $('.wk_2checkout_loader').show();
                     $(window).load(function() {
                        $(".wk_2checkout_loader").delay(3000).animate({
                            opacity:0,
                            width: 0,
                            height:0
                        }, 500);

                    });
                });
             }

            var errorCallback = function(data) {
                if (data.errorCode === 200) {
                    tokenRequest();
                } else {
                    console.log('errr');
                    alert(data.errorMsg);
                }
            };

            var tokenRequest = function(sellerId,publishableKey) {
                var args = {
                    sellerId: sellerId,
                    publishableKey: publishableKey,
                    ccNo: $("#wk_2checkout_credit_card_number_4").val()+$("#wk_2checkout_credit_card_number_8").val()+$("#wk_2checkout_credit_card_number_12").val()+$("#wk_2checkout_credit_card_number_16").val(),
                    cvv: $("#wk_2checkout_credit_card_cvv").val(),
                    expMonth: $("#wk_2checkout_credit_card_expMonth").val(),
                    expYear: $("#wk_2checkout_credit_card_expYear").val()
                };

                TCO.requestToken(submit_2checkout_payment_odoo, errorCallback, args);
            };

                $('#payment_2checkout_submit').on('click',function(){
                $('#wk_2checkout_myModal').appendTo('body').modal('show');
            });
                   $("#2checkout_payment_form").submit(function(event) {
                     $('.submit-button').attr("disabled", "disabled");
                    var sellerId=$('#submit_2checkout_payment').data('sellerid');
                    var publishableKey=$('#submit_2checkout_payment').data('publishablekey');
                    tokenRequest(sellerId,publishableKey);
                    return false;
                });




        });

});
