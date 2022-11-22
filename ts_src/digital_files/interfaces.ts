import {MessageType} from "./consts";

export interface IFile {
    upload_date: string;
    clean_name: string;
    id: number;
    file_size: string;
}

export interface IDownloadable {
    id: number;
    folder_contents?: IDownloadable[];
    last_download_date?: string;
    updated_timestamp: string;
    file?: IFile;
    name: string;

}

export interface returnMessage {
    message_type: MessageType;
    element_id: string;
    text?: string;
    progress?: number;
    filename?: string;
    url?: string;
    file_buffer?: ArrayBuffer;
    in_flight_downloads?: number;
}

export interface downloadFileParameters {
    element_id: string;
    product_slug: string;
    orig_text: string;
    di_id: string;
    di_file_id: string;
    size: number;
}

export interface requestMessage {
    message_type: string;
    pack_id?: string;
    downloadable_id?: string;
    di_id?: string;
    files?: Array<downloadFileParameters>;
    products?: Array<downloadProductParams>;
    filename?: string;
    clicked_element_id?: string;
    orig_text?: string;
}

export interface fileReturn {
    file?: ArrayBuffer;
    filename: string;
    url?: string;
}


export interface downloadProductParams {
    filename: string;
    di_id: string;
    downloadable_id: string;
}


export interface serverFileResponse {
    clean_name: string,
    comment_stamp: string,
    seed1: string,
    seed2: string,
    userid: string,
    tz: boolean,
    to: boolean,
}