// Custom component to wrap the PayPalButtons and handle currency changes
import * as React from "react";
import {useCallback, useEffect} from "react";
import {PayPalButtons, usePayPalScriptReducer} from "@paypal/react-paypal-js";
import getCookie from "../../../cart/components/get_cookie";
import {iPaymentMethod} from "../interfaces";


const PaypalPaymentForm: React.FunctionComponent<iPaymentMethod> = (props): JSX.Element => {
    // usePayPalScriptReducer can be use only inside children of PayPalScriptProviders
    // This is the main reason to wrap the PayPalButtons in a new component
    const [{options, isPending}, dispatch] = usePayPalScriptReducer();
    const showSpinner = false;
    useEffect(() => {
        dispatch({
            type: "resetOptions",
            value: {
                ...options,
            },
        });
    }, [showSpinner]);

    function createOrder(data: any, actions: any) {
        return fetch("/checkout/create_paypal_payment/", {
            method: "post",
            headers: {
                'X-CSRFToken': getCookie("csrftoken")
            }

        })
            .then((response) => response.json())
            .then((order) => order.id);
    }

    // let the server know we're paying for the cart
    const onApprove = useCallback((data: any, actions: any) => {
        return fetch(`/checkout/capture_paypal_payment/${data.orderID}/`, {
            method: "post",
        })
            .then((response) => response.json())
            .then((orderData) => {
                // Three cases to handle:
                //   (1) Recoverable INSTRUMENT_DECLINED -> call actions.restart()
                //   (2) Other non-recoverable errors -> Show a failure message
                //   (3) Successful transaction -> Show confirmation or thank you

                // This example reads a v2/checkout/orders capture response, propagated from the server
                // You could use a different API or structure for your 'orderData'
                var errorDetail = Array.isArray(orderData.details) && orderData.details[0];

                if (errorDetail && errorDetail.issue === 'INSTRUMENT_DECLINED') {
                    return actions.restart(); // Recoverable state, per:
                    // https://developer.paypal.com/docs/checkout/integration-features/funding-failure/
                }
                const element = document.getElementById('paypal-button-container');

                if (errorDetail) {
                    var msg = 'Sorry, your transaction could not be processed.';
                    if (errorDetail.description) msg += '\n\n' + errorDetail.description;
                    if (orderData.debug_id) msg += ' (' + orderData.debug_id + ')';
                    element.innerHTML = msg; // Show a failure message
                    return
                }

                // Successful capture!
                console.log('Capture result', orderData, JSON.stringify(orderData, null, 2));
                const transaction = orderData.purchase_units[0].payments.captures[0];
                element.innerHTML = '<h3>Thank you for your payment!</h3>';
                props.success_action();
            })
    }, [])


    return (<div id={'paypal-button-container'}>
            {(showSpinner && isPending) && <i className="fas fa-spinner fa-pulse"></i>}
            <PayPalButtons style={{layout: "vertical"}}
                           createOrder={createOrder}
                           onApprove={onApprove}
            />
        </div>
    );
}
export default PaypalPaymentForm;