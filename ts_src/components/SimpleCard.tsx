import * as React from "react";

interface iSimpleCardProps{
    className?: string
}

const SimpleCard: React.FunctionComponent<React.PropsWithChildren<iSimpleCardProps>> = (props): JSX.Element => {
    return <div
        className={`w-full py-2 bg-gray-50 border border-gray-300 xl:bg-white px-4 xl:py-4 rounded-md self-start shadow ${props.className}`}>
        {props.children}
    </div>
}

export default SimpleCard;