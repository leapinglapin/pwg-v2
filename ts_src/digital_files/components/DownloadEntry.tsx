import * as React from "react";
import {useState} from "react";
import {IDownloadable} from "../interfaces";

export interface IDownloadEntryProps {
    downloadable: IDownloadable;
    indent?: number;
    hide?: boolean;

}

export const DownloadEntry: React.FunctionComponent<IDownloadEntryProps> = (
    props: IDownloadEntryProps
): JSX.Element => {

    let indent = props.indent
    const is_root_folder = props.indent == undefined
    if (is_root_folder) {
        indent = -1; //Ensure the first row has no indent
    }
    let [expanded, set_expanded] = useState(indent < 0) // First visible row should start expanded

    const downlaoded_date = props.downloadable.last_download_date ?
        (new Date(props.downloadable.last_download_date)).toLocaleDateString() : "";

    const updated_date = props.downloadable.updated_timestamp ?
        (new Date(props.downloadable.updated_timestamp)).toLocaleDateString() : "";

    const DISP_NONE = {display: 'none'}
    const row = <tr style={props.hide ? DISP_NONE : null}>
        <td className={"w-5/8"}>
            {">".repeat(props.indent)}{props.downloadable.name}
            {props.downloadable.file ? <></> : //Folder
                <button className='folder_expand {{ recursive_button_class }} btn btn-secondary' type="button"
                        onClick={() => set_expanded(!expanded)}>
                    {expanded ? "Collapse" : "Expand"}
                </button>
            }
        </td>
        <td className={"w-1/8"}>
            {props.downloadable.file ?
                <>{props.downloadable.file.file_size} B</> :
                <>{props.downloadable.folder_contents.length} items</>}
        </td>
        <td className={"w-1/8"}>
            {downlaoded_date}
        </td>
        <td className={"w-1/8"}>
            {updated_date}
        </td>
    </tr>

    if (props.downloadable.file) {
        return row
    } else {
        const entry_rows = props.downloadable.folder_contents.map((downloadable) => {
            return <DownloadEntry downloadable={downloadable} indent={indent + 1} hide={!expanded}/>
        })
        return <>
            {is_root_folder ? <></> : row}
            {entry_rows}
        </>
    }

}
