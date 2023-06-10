import * as React from "react";
import {ChangeEvent, FormEvent, useEffect, useState} from "react";
import getCookie from "../../cart/components/get_cookie";
import {updateCart} from "../../cart/reducers/cartSlice";
import {iCheckoutForm} from "./interfaces";
import {useSelector} from "react-redux";
import {RootState, useAppDispatch} from "../../cart/store";
import SimpleCard from "../../components/SimpleCard";


const CheckoutEmailForm: React.FunctionComponent<iCheckoutForm> = (props): JSX.Element => {
    const currentCart = useSelector((state: RootState) => state.cart.cart);
    var dispatch = useAppDispatch();
    let [email, setEmail] = useState(currentCart.owner_info)

    useEffect(() => {
        // Update the document title using the browser API
        props.setSummary(summary())
    });

    function handleEmailChange(event: ChangeEvent<HTMLInputElement>) {
        setEmail(event.target.value);
    }

    async function submitEmail(event: FormEvent) {
        event.preventDefault()
        let response = await fetch(
            `/cart/api/set/email/`,
            {
                method: "post",
                body: JSON.stringify({
                    email: email,
                }),
                headers: {"X-CSRFToken": getCookie("csrftoken")},
            }
        );

        if (response.ok) {
            dispatch(updateCart());
            console.log("Set email!")
        } else {
            let text = await response.text();
            throw new Error("Request Failed: " + text);
        }
    }

    function summary(): string {
        if (!currentCart.email) {
            return "Login or Email Required"
        }
        if (currentCart.username) {
            return "Logged in as " + currentCart.username

        }
        return "Checking out as " + currentCart.email
    }

    useEffect(() => {
        setEmail(currentCart.email)
        props.setSummary(summary())
    }, [currentCart.email, currentCart.username])

    if (currentCart.username) {
        return <SimpleCard>
            You are currently logged in as {currentCart.username}
        </SimpleCard>
    } else {
        return <SimpleCard>

            <button className={"btn btn-primary"} onClick={() => {
                window.location.href = '/accounts/login/?next=/checkout/v2/'
            }}> Login
            </button>
            <button className={"btn btn-secondary"} onClick={() => {
                window.location.href = '/accounts/signup/?next=/checkout/v2/'
            }}> Sign Up
            </button>
            {currentCart.is_account_required ? "You must log in or sign up to purchase these products" :
                <form onSubmit={submitEmail}>
                    <input type="email" name="email" maxLength={254} required={true} onChange={handleEmailChange}
                           value={currentCart.email}>

                    </input>
                    <button className={"btn btn-primary"} onClick={() => {
                    }}> Continue as guest
                    </button>
                </form>
            }
        </SimpleCard>
    }
}


export default CheckoutEmailForm;