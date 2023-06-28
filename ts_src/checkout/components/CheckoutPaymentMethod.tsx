import * as React from "react";
import {useCallback, useEffect, useState} from "react";
import {iCheckoutForm} from "./interfaces";
import getCookie from "../../cart/components/get_cookie";
import {RootState, useAppDispatch} from "../../cart/store";
import {useSelector} from "react-redux";
import {Elements} from "@stripe/react-stripe-js";

import {Appearance, loadStripe, StripeElementsOptions} from "@stripe/stripe-js";
import StripePaymentForm from "./PaymentMethods/StripePaymentForm";
import PaypalPaymentForm from "./PaymentMethods/PaypalPaymentForm";
import {PayPalScriptProvider} from "@paypal/react-paypal-js";
import type {PayPalScriptOptions} from "@paypal/paypal-js";

import SimpleCard from "../../components/SimpleCard";
import {gap} from "../../components/ui_constants";

const req = new XMLHttpRequest();
req.open("GET", "/checkout/payment_api_info/", false);
req.send()
const api_data = JSON.parse(req.response)
const paypal_client_id = api_data.PAYPAL_CLIENT_ID
const stripePromise = loadStripe(api_data.STRIPE_PUBLIC_KEY);

const CheckoutPaymentMethod: React.FunctionComponent<iCheckoutForm> = (props): JSX.Element => {
    const currentCart = useSelector((state: RootState) => state.cart.cart);
    var dispatch = useAppDispatch();

    const [savedCartID, setSavedCartID] = useState(null)
    const [loading, setLoading] = useState(false)
    const [errorText, setErrorText] = useState("")

    useEffect(() => {
        props.setSummary(summary())
    }, [currentCart.delivery_method, currentCart.pickup_partner, currentCart.shipping_address]);

    function summary(): string {
        return "Choose a method of payment";
    }

    useEffect(() => {
        // If somehow, the user is still on the cart and the status is paid, redirect to the success page
        if (currentCart.status in ["Submitted", "Paid", "Completed", "Cancelled"]) {
            redirect_to_success_page()
        }
        // Redirect user to success page if a new cart is made during the current session.
        if (currentCart.id && savedCartID && currentCart.id != savedCartID) {
            window.location.assign(`/checkout/complete/${savedCartID}`)
        }
        if (currentCart.id && savedCartID == null) {
            setSavedCartID(currentCart.id)
        }

    }, [currentCart.id, currentCart.status])

    const redirect_to_success_page = useCallback(() => {
        window.location.assign(`/checkout/complete/${currentCart.id}`)
    }, [currentCart.id])

    async function setPayAtLocation() {
        setLoading(true)
        try {
            let response = await fetch(
                "/checkout/pay_at_pickup_location/",
                {
                    method: "post",
                    headers: {"X-CSRFToken": getCookie("csrftoken")},
                }
            );
            if (response.ok) {
                console.log("Set Payment Location!")
                redirect_to_success_page();
            } else {
                let text = await response.text();
                throw new Error("Request Failed: " + text);
            }
        } catch (exception) {
            setErrorText(exception.toString())
            setLoading(false);
        }
    }

    async function markFreePaid() {
        setLoading(true)
        try {
            let response = await fetch(
                "/cart/api/set/mark_free_as_paid/",
                {
                    method: "post",
                    headers: {"X-CSRFToken": getCookie("csrftoken")},
                }
            );
            if (response.ok) {
                console.log("Marked order as paid!")
                redirect_to_success_page();
            } else {
                let text = await response.text();
                throw new Error("Request Failed: " + text);
            }
        } catch (exception) {
            setErrorText(exception.toString())
            setLoading(false);
        }
    }


    const [clientSecret, setClientSecret] = useState("");

    useEffect(() => {
        setClientSecret("") // Clear value if we are reloading for a delivery method change.
        // Create PaymentIntent as soon as the page loads
        fetch("/checkout/create_stripe_payment/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                'X-CSRFToken': getCookie("csrftoken")
            },
        })
            .then((res) => res.json())
            .then((data) => setClientSecret(data.clientSecret));
    }, [currentCart.delivery_method]); // Update when the billing address changes.

    const appearance: Appearance = {
        theme: 'stripe'
    };
    const stripeOptions: StripeElementsOptions = {
        clientSecret,
        appearance,
    };

    const paypalOptions: PayPalScriptOptions = {
        "client-id": paypal_client_id,
        "enable-funding": "venmo",
        "disable-funding": "paylater",
    };


    return <div className={`grid grid-flow-row auto-rows-max ${gap}`}>
        {currentCart.is_free ?
            <SimpleCard>
                <p>
                    Your order is free!
                </p>
                {loading ?
                    <div className="fa fa-spinner fa-pulse" id="spinner"></div> :
                    errorText ? <p>{errorText}</p> :
                        <button type="submit" className="btn btn-primary" onClick={markFreePaid}>
                            Submit
                        </button>
                }
            </SimpleCard>
            :
            <React.Fragment>
                <SimpleCard className="col-span-2">
                    {clientSecret && (
                        <Elements options={stripeOptions} stripe={stripePromise}>
                            <StripePaymentForm clientSecret={clientSecret}
                                               redirectToSuccessPage={redirect_to_success_page}/>
                        </Elements>
                    )}
                </SimpleCard>
                {currentCart.pickup_partner ?
                    <SimpleCard>
                        {loading ?
                            <div className="fa fa-spinner fa-pulse" id="spinner"></div> :
                            errorText ? <p>{errorText}</p> :
                                <button type="submit" className="btn btn-primary" onClick={setPayAtLocation}>
                                    Pay at {currentCart?.pickup_partner?.name}
                                </button>
                        }
                    </SimpleCard>
                    : ""}
                <SimpleCard className={currentCart.pickup_partner ? "" : "col-span-2"}>
                    <PayPalScriptProvider options={paypalOptions}>
                        <PaypalPaymentForm cart_id={currentCart.id} success_action={redirect_to_success_page}/>
                    </PayPalScriptProvider>
                </SimpleCard>
            </React.Fragment>
        }
    </div>
}


export default CheckoutPaymentMethod;