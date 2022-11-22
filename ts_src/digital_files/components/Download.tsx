import * as React from "react";
import {IDownloadable} from "../interfaces";
import {DownloadEntry} from "./DownloadEntry";

export interface IDownloadProps {
    downloadable: IDownloadable;
}

export const Download: React.FunctionComponent<IDownloadProps> = (
    props: IDownloadProps
): JSX.Element => {
    return <table>
        <tr className={"text-gray-500 align-text-bottom align-bottom"}>
            <th className={"font-semibold w-5/8"}>File</th>
            <th className={"font-semibold w-1/8"}>Size</th>
            <th className={"font-semibold w-1/8"}>Last <br/> Downloaded</th>
            <th className={"font-semibold w-1/8"}>Last <br/> Updated</th>
        </tr>
        <DownloadEntry downloadable={props.downloadable} />
    </table>

}
