import * as React from "react";
import { useState } from "react";

export interface IProductListPageSortProps {
    choices: string[][];
    currentValue: string;
    name: string;
    id: string;
}

const ProductListPageSort: React.FunctionComponent<IProductListPageSortProps> = (
    props: IProductListPageSortProps
): JSX.Element => {
    let [choice, setChoice] = useState(props.currentValue);
    console.log(props);

    const isSortedDescending = (choiceKey: string) => {
        return choiceKey.startsWith("-");
    };

    const options = props.choices.map((iChoice) => {
        return <option value={iChoice[0]}>{iChoice[1]}</option>;
        // if (iChoice[0] == choice) humanChoiceName = iChoice[1];
    });

    let icon;

    if (isSortedDescending(choice)) {
        icon = (
            <svg
                id="order_by_sort_descending"
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 text-gray-400"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
            >
                <path d="M3 3a1 1 0 000 2h11a1 1 0 100-2H3zM3 7a1 1 0 000 2h7a1 1 0 100-2H3zM3 11a1 1 0 100 2h4a1 1 0 100-2H3zM15 8a1 1 0 10-2 0v5.586l-1.293-1.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L15 13.586V8z" />
            </svg>
        );
    } else {
        icon = (
            <svg
                id="order_by_sort_ascending"
                className="h-5 w-5 text-gray-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
            >
                <path d="M3 3a1 1 0 000 2h11a1 1 0 100-2H3zM3 7a1 1 0 000 2h5a1 1 0 000-2H3zM3 11a1 1 0 100 2h4a1 1 0 100-2H3zM13 16a1 1 0 102 0v-5.586l1.293 1.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 101.414 1.414L13 10.414V16z" />
            </svg>
        );
    }

    return (
        <>
            <select
                id={props.id}
                name={props.name}
                value={choice}
                onChange={(e) => {
                    setChoice(e.target.value);
                    (document.getElementById(
                        "filter_form"
                    ) as HTMLFormElement).submit();
                }}
                className="reset-select pl-4 pr-8 py-2 border border-gray-300 font-medium rounded-md text-gray-700 bg-gray-50 hover:bg-gray-100 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 shadow"
            >
                {options}
            </select>
            {/* <button className="-ml-px relative inline-flex items-center space-x-2 px-4 py-2 border border-gray-300 font-medium rounded-md text-gray-700 bg-gray-50 hover:bg-gray-100 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 shadow">
                {icon}
                <span id="order_by_label">{humanChoiceName}</span>
            </button>
            <input
                type="hidden"
                name={props.name}
                id={props.id}
                value={choice}
            /> */}
        </>
    );
};

export default ProductListPageSort;
