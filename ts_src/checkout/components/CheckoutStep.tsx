import * as React from "react";
import {Dispatch, SetStateAction, useCallback, useEffect, useState} from "react";
import {useSelector} from "react-redux";
import {RootState} from "../../cart/store";

// Keep in sync with checkout/models.py
export enum step {
    START = 0,
    LOGIN,
    DELIVERY_METHOD,
    PAYMENT_COLLECTION,

}

interface IStepParams {
    title: string;
    id: step;
    current_section: step;
    summary: string;
    setSection: Dispatch<SetStateAction<step>>
    is_sidebar?: boolean;
}


const CheckoutStep: React.FunctionComponent<React.PropsWithChildren<IStepParams>> = (props): JSX.Element => {
    const [showing, setShowing] = useState(false)
    const cart = useSelector((state: RootState) => state.cart.cart);


    const [ready, setReady] = useState(false);
    useEffect(() => {
        setReady(Array.isArray(cart.ready_steps) ? cart.ready_steps.includes(props.id) : false)
    }, [cart.ready_steps])
    const completed = Array.isArray(cart.completed_steps) ? cart.completed_steps.includes(props.id) : false;

    const selectSection = useCallback(() => {
        if (props.is_sidebar || !ready) {
            return //Don't do anything when clicked on large windows
        }
        let oldState = props.current_section
        props.setSection(props.id) //This should cause the section to show?
        if (oldState == props.id) { // If we are the current section, toggle back and forth
            setShowing(!showing)
        }
    }, [props.is_sidebar, props.current_section, showing, ready])

    useEffect(() => {
            setShowing(props.is_sidebar || (props.current_section == props.id) || (props.id == step.START && !cart.status))
        },
        [props.current_section, props.is_sidebar]
    )

    const className = "py-2" + " " + (props.is_sidebar ? "w-full xl:w-auto" : "w-full");


    return <div className={className}>
        <div onClick={selectSection}
             className={`flex flex-row w-full justify-between cursor-pointer py-2 border border-gray-300 px-4 xl:py-4 rounded-md self-start shadow
             ${ready ? (completed ? "bg-green-200" : "bg-white") : "bg-gray-100"}`}>
            <div className={"flex flex-row gap-1 "}>
                <div className="font-bold">{props.title}</div>
                {!ready ?
                    <div className="text-gray-700 font_small inline">Please complete the above steps first</div> :
                    <div className="text-gray-700 font_small inline">{props.summary}</div>
                }
            </div>
            {!props.is_sidebar && ready ? <React.Fragment>
                    <svg xmlns="http://www.w3.org/2000/svg" id="filtersChevron"
                         className={`h-6 w-6 text-gray-600 ${showing ? "" : "transform rotate-180"}`}
                         fill="none" viewBox="0 0 24 24"
                         stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
                              d="M19 13l-7 7-7-7m14-8l-7 7-7-7">

                        </path>
                    </svg>
                </React.Fragment>

                : ""}
        </div>
        <div hidden={!showing} className={"py-2 px-4 xl:py-4"}>
            {ready ? props.children : ""}
        </div>
    </div>
}

export default CheckoutStep;