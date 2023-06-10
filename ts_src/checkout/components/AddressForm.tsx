import * as React from "react";
import {FormEvent, useEffect, useState} from "react";
import getCookie from "../../cart/components/get_cookie";
import {updateCart} from "../../cart/reducers/cartSlice";
import {IAddress} from "../../cart/interfaces";
import CountryInput from "./CountryInput";
import {RootState, useAppDispatch} from "../../cart/store";
import {useSelector} from "react-redux";
import {gap} from "../../components/ui_constants";


interface IAddressForm {
    address: IAddress;
    phoneRequired: boolean;
    limit_country_options?: boolean;
    endpoint: string;
}

const AddressForm: React.FunctionComponent<IAddressForm> = (props): JSX.Element => {
    const dispatch = useAppDispatch();
    const currentCart = useSelector((state: RootState) => state.cart.cart);
    const [firstName, setFirstName] = useState(props.address?.first_name)
    const [lastName, setLastName] = useState(props.address?.last_name)
    const [line1, setLine1] = useState(props.address?.line1)
    const [line2, setLine2] = useState(props.address?.line2)
    const [line3, setLine3] = useState(props.address?.line3)
    const [line4, setLine4] = useState(props.address?.line4)
    const [state, setState] = useState(props.address?.state)
    const [postcode, setPostcode] = useState(props.address?.postcode)
    const [phone, setPhone] = useState(props.address?.phone_number)

    const [loading, setLoading] = useState(false)

    useEffect(() => {
        setFirstName(props.address?.first_name)
        setLastName(props.address?.last_name)
        setLine1(props.address?.line1)
        setLine2(props.address?.line2)
        setLine3(props.address?.line3)
        setLine4(props.address?.line4)
        setState(props.address?.state)
        setPostcode(props.address?.postcode)
        setPhone(props.address?.phone_number)

    }, [props.address])

    async function setAddress(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        setLoading(true);
        const data = new FormData(event.target as HTMLFormElement);
        let response = await fetch(
            props.endpoint,
            {
                method: "post",
                body: data,
                headers: {"X-CSRFToken": getCookie("csrftoken")},
            }
        );

        if (response.ok) {
            dispatch(updateCart());
            console.log("Set Address!")
            setLoading(false)
        } else {
            let text = await response.text();
            throw new Error("Request Failed: " + text);
        }
    }

    return <>
        <form onSubmit={setAddress}>
            <div className="grid grid-cols-2-auto items-center justify-items-stretch gap-3 text-sm">
                <FormComponent maxLength={255} component_name={"first_name"} label={"First Name:"}
                               required={true} value={firstName} set_function={setFirstName}/>
                <FormComponent maxLength={255} component_name={"last_name"} label={"Last Name:"}
                               required={true} value={lastName} set_function={setLastName}/>
                <FormComponent maxLength={255} component_name={"line1"} label={"First line of address:"}
                               required={true} value={line1} set_function={setLine1}/>
                <FormComponent maxLength={255} component_name={"line2"} label={"Second line of address:"}
                               required={false} value={line2} set_function={setLine2}/>
                <FormComponent maxLength={255} component_name={"line3"} label={"Third line of address:"}
                               required={false} value={line3} set_function={setLine3}/>
                <FormComponent maxLength={255} component_name={"line4"} label={"City:"}
                               required={true} value={line4} set_function={setLine4}/>
                <FormComponent maxLength={255} component_name={"state"} label={"State:"}
                               required={false} value={state} set_function={setState}/>
                <FormComponent maxLength={64} component_name={"postcode"} label={"Post/Zip-code:"}
                               required={true} value={postcode} set_function={setPostcode}/>
                <label htmlFor="id_country">Country: <span>*</span></label>
                <CountryInput selected_country={props.address?.country}
                              limit_country_options={props.limit_country_options}/>
                <FormComponent maxLength={128} component_name={"phone_number"} label={"Phone Number:"}
                               required={props.phoneRequired} value={phone} set_function={setPhone}/>
            </div>
            <div className={`flex justify-end ${gap}`}>
                {loading ? <i className="fas fa-spinner fa-pulse"></i> :
                    <button type="submit" className="btn btn-primary">
                        {currentCart.is_shipping_required ? "Ship to this Address" : "Set Billing Address"}
                    </button>}
            </div>
        </form>
    </>
}

interface IFormComponentProp {
    maxLength: number
    component_name: string
    label: string
    required: boolean
    value: string
    set_function: React.Dispatch<React.SetStateAction<string>>
}

const FormComponent: React.FunctionComponent<IFormComponentProp> = (props): JSX.Element => {
    const currentCart = useSelector((state: RootState) => state.cart.cart);
    let err_msg = null;
    if (currentCart.address_error != null) {
        const err_str = JSON.parse(currentCart.address_error)
        const errs = JSON.parse(err_str)
        if (errs && typeof(errs) == 'object' &&  props.component_name in errs) {
            err_msg = errs[props.component_name][0]['message']
        }
    }
    const className = 'form-input rounded-md ' + err_msg ? "is-invalid" : "";
    const id = "id_" + props.component_name;
    return <React.Fragment>
        <label htmlFor={id}>{props.label} {props.required && <span>*</span>} </label>
        <div>
            <input type="text"
                   className={className}
                   name={props.component_name}
                   maxLength={props.maxLength} required={props.required}
                   value={props.value}
                   onChange={(e) => (props.set_function(e.target.value))}
                   id={id}/>
            {err_msg && <div className="invalid-feedback">
                {err_msg}
            </div>}
        </div>
    </React.Fragment>
}


export default AddressForm;