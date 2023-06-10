import * as React from "react";
import {FormEventHandler, useEffect, useState} from "react";

import {PaymentElement, useElements, useStripe} from "@stripe/react-stripe-js";
import {useSelector} from "react-redux";
import {RootState} from "../../../cart/store";

declare var ENV_PROTOCOL: string; //Replaced by webpack

interface stripeProps {
    clientSecret: string
    redirectToSuccessPage: () => any
}

const StripePaymentForm: React.FunctionComponent<stripeProps> = (props): JSX.Element => {
    const stripe = useStripe();
    const elements = useElements();
    const currentCart = useSelector((state: RootState) => state.cart.cart);

    const [message, setMessage] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    // Double check status of cart isn't successful already
    useEffect(() => {
        if (!stripe) {
            return;
        }
        const clientSecret = props.clientSecret;
        stripe.retrievePaymentIntent(clientSecret).then(({paymentIntent}) => {
            switch (paymentIntent.status) {
                case "succeeded":
                    setMessage("Payment succeeded!");
                    props.redirectToSuccessPage()
                    break;
            }
        })
    }, [stripe, props.clientSecret])

    // For when stripe redirects the user to this page.
    useEffect(() => {
        if (!stripe) {
            return;
        }
        const clientSecret = new URLSearchParams(window.location.search).get(
            "payment_intent_client_secret"
        );
        if (!clientSecret) {
            return;
        }

        stripe.retrievePaymentIntent(clientSecret).then(({paymentIntent}) => {
            switch (paymentIntent.status) {
                case "succeeded":
                    setMessage("Payment succeeded!");
                    props.redirectToSuccessPage()
                    break;
                case "processing":
                    setMessage("Your payment is processing.");
                    break;
                case "requires_payment_method":
                    setMessage("Your payment was not successful, please try again.");
                    break;
                default:
                    setMessage("Something went wrong.");
                    break;
            }
        });
    }, [stripe]);

    const handleSubmit: FormEventHandler<HTMLFormElement> = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        if (!stripe || !elements) {
            // Stripe.js has not yet loaded.
            // Make sure to disable form submission until Stripe.js has loaded.
            return;
        }

        setIsLoading(true);

        const {error} = await stripe.confirmPayment({
            elements,
            confirmParams: {
                // Env Protocol is HTTPS in production, but HTTP for local testing.
                return_url: `${ENV_PROTOCOL}${currentCart.site}/checkout/confirm_stripe_capture/`,
            },
        });

        // This point will only be reached if there is an immediate error when
        // confirming the payment. Otherwise, your customer will be redirected to
        // your `return_url`. For some payment methods like iDEAL, your customer will
        // be redirected to an intermediate site first to authorize the payment, then
        // redirected to the `return_url`.
        if (error.type === "card_error" || error.type === "validation_error") {
            setMessage(error.message);
        } else {
            setMessage("An unexpected error occurred.");
        }

        setIsLoading(false);
    };


    return (
        <form id="payment-form" onSubmit={handleSubmit}>
            <PaymentElement id="payment-element"/>
            <div className="flex justify-end py-2">
                <button className="btn btn-primary" disabled={isLoading || !stripe || !elements} id="submit">
                <span id="button-text">
                  {isLoading ? <i className="fas fa-spinner fa-pulse"></i> : "Pay now"}
                </span>
                </button>
            </div>
            {/* Show any error or success messages */}
            {message && <div id="payment-message">{message}</div>}
        </form>
    );

}

export default StripePaymentForm;