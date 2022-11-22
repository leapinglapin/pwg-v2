import * as React from "react";
import {FormEvent, useEffect, useState} from "react";

import {IPOSProps} from "../interfaces";
import POSPayment from "./POSPayment"
import CartBody from "./CartBody";
import CartSelector from "./CartSelector";
import getCookie from "./get_cookie";
import {RootState, useAppDispatch} from "../store";
import {
    addCustomPOSItem,
    addNewPOSItem,
    removeFromCart,
    setPOS,
    setPOSOwner,
    updateLine,
} from "../reducers/cartSlice";
import {useSelector} from "react-redux";

const POS: React.FunctionComponent<IPOSProps> = (props: IPOSProps): JSX.Element => {
    const dispatch = useAppDispatch();
    const currentStatus = useSelector((state: RootState) => state.cart.pos);

    useEffect(() => {
        dispatch(setPOS(props));
    }, [props]);


    React.useEffect(() => {
        if (currentStatus.active_cart && currentStatus.active_cart.id) {
            window.history.replaceState(
                null,
                "",
                `${currentStatus.url}/${currentStatus.active_cart.id}/`
            );
        }
    }, [currentStatus.active_cart]);

    const HandleScan = (event: CustomEvent) => { // Alternative to document.addEventListener('scan')
        let sCode = event.detail.scanCode
        AddItem(sCode)

    }

    const HandleAdd = (event: FormEvent) => {
        event.preventDefault()
        const data = new FormData(event.target as HTMLFormElement);
        AddItem(data.get('barcode') as string)

    }


    const AddItem = (barcode: string) => {
        dispatch(
            addNewPOSItem({
                barcode,
            })
        );
    }

    const HandleCustom = (event: FormEvent) => {
        event.preventDefault()
        const data = new FormData(event.target as HTMLFormElement);
        dispatch(
            addCustomPOSItem({
                description: data.get("description") as string,
                price: Number(data.get("price") as string),
            })
        );
    }


    const HandleOwner = (event: FormEvent) => {
        event.preventDefault()
        const data = new FormData(event.target as HTMLFormElement);
        dispatch(
            setPOSOwner({
                email: data.get("email") as string,
            })
        );
    }

    React.useEffect(() => {
        document.addEventListener('scan', HandleScan)
        return function cleanup() {
            document.removeEventListener("scan", HandleScan);
        }
    }, [HandleScan]); // <--- This hook is called only once


    return (
        <>
            <div className="flex flex-row">
                <div>
                    <POSPayment
                        base_url={props.url}
                        cart={currentStatus.active_cart}
                    />
                    <CartSelector/>
                </div>
                <div>
                    {currentStatus.active_cart &&
                    currentStatus.active_cart.id ? (
                        <>
                            <h1>
                                {" "}
                                Cart Number: {currentStatus.active_cart.id}{" "}
                                <input type={"number"} step='1' id={'id_cart_id'} hidden={true} readOnly={true}
                                       value={currentStatus.active_cart.id}>
                                </input>
                            </h1>
                            {currentStatus.active_cart.status}
                            {currentStatus.active_cart.open ? (
                                <>
                                    {currentStatus.active_cart.owner_info ==
                                    null ? (
                                        <form onSubmit={HandleOwner}>
                                            <label>
                                                Email:
                                                <input
                                                    type="text"
                                                    name="email"
                                                />
                                            </label>
                                            <input type="submit" value="Set"/>
                                        </form>
                                    ) : (
                                        <p>
                                            {" "}
                                            Owner:{" "}
                                            {
                                                currentStatus.active_cart
                                                    .owner_info
                                            }{" "}
                                        </p>
                                    )}

                                    <form onSubmit={HandleAdd}>
                                        <h3>Add Item (Or Scan):</h3>
                                        <label>
                                            Barcode:
                                            <input type="text" name="barcode"/>
                                        </label>
                                        <input type="submit" value="Add"/>
                                    </form>
                                    <form onSubmit={HandleCustom}>
                                        <h3>Add Custom Item:</h3>
                                        <label>
                                            Description:
                                            <input
                                                type="text"
                                                name="description"
                                            />
                                        </label>
                                        <label>
                                            Price:
                                            <input
                                                type="number"
                                                name="price"
                                                step=".01"
                                            />
                                        </label>
                                        <input type="submit" value="Add"/>
                                    </form>
                                </>
                            ) : (
                                <></>
                            )}
                            <CartBody
                                cart={currentStatus.active_cart}
                                full={true}
                                pos={true}
                            />
                        </>
                    ) : (
                        <></>
                    )}
                </div>
            </div>
        </>
    );
};

export default POS
