import * as JSZip from "jszip";


import {
    downloadFileParameters,
    downloadProductParams,
    fileReturn,
    requestMessage,
    returnMessage,
    serverFileResponse
} from "./interfaces"
import {MessageType as MT} from "./consts";


const port: Worker = self as any;

const version = "6.00"
let in_flight_actions = 0;
console.log("Version " + version)

port.onmessage = function (e) {
    let request_message = <requestMessage>e.data
    console.log(request_message)
    switch (request_message.message_type) {
        case "Single":
            console.log("I will download a single file");
            if (request_message.files.length == 1) {
                let file_params = request_message.files[0]
                in_flight_actions += 1;
                Download(file_params).then((returned_info) => {
                    let message: returnMessage
                    if (returned_info.url) {
                        message = {
                            message_type: MT.url,
                            element_id: file_params.element_id,
                            text: file_params.orig_text + "is Downloading",
                            url: returned_info.url,
                            filename: returned_info.filename,
                        }
                        port.postMessage(message)
                    } else {
                        message = {
                            message_type: MT.file,
                            element_id: file_params.element_id,
                            text: file_params.orig_text + " Done",
                            progress: 1,
                            file_buffer: returned_info.file,
                            filename: returned_info.filename,
                        }
                        port.postMessage(message, [returned_info.file])

                    }
                    decrement_in_flight_count();
                })
            } else {
                console.log("I was sent more than one file for a single file request")
            }
            break;
        case "Multiple":
            console.log("I will download multiple files");
            in_flight_actions += 1;
            Download_Multiple(request_message.clicked_element_id, request_message.filename, request_message.downloadable_id, request_message.orig_text, request_message.di_id).then((files_to_return) => {
                    let message: returnMessage = {
                        message_type: MT.file,
                        element_id: request_message.clicked_element_id,
                        text: request_message.orig_text + " Done",
                        progress: 1,
                        file_buffer: files_to_return.file,
                        filename: request_message.filename + ".zip",
                    }
                    port.postMessage(message, [files_to_return.file])
                    decrement_in_flight_count();
                }
            )
            break;
        case "Pack":
            console.log("I will download multiple products");
            in_flight_actions += 1;
            Download_Pack(request_message.clicked_element_id, request_message.orig_text, request_message.products).then(() => {
                    let status_message: returnMessage = {
                        message_type: MT.progress,
                        element_id: request_message.clicked_element_id,
                        text: request_message.orig_text + " Done",
                        progress: 1,
                    }
                    port.postMessage(status_message)
                    decrement_in_flight_count();
                }
            )
            break;
        default:
            console.log("I was sent " + request_message.message_type + " which is not a valid download type");

    }
}

function decrement_in_flight_count() {
    in_flight_actions -= 1;
    console.log("In flight downloads", in_flight_actions);
    let status_message: returnMessage = {
        message_type: MT.download_status_update,
        in_flight_downloads: in_flight_actions,
        element_id: null
    };
    port.postMessage(status_message);
}

async function Download_Pack(clicked_element_id: string, orig_text: string, products: Array<downloadProductParams>) {
    let total_products = products.length
    let count = 0
    for (const download_params of products) {
        let status_message: returnMessage = {
            message_type: MT.progress,
            element_id: clicked_element_id,
            text: orig_text + " Downloading",
            progress: count / total_products,
        }
        port.postMessage(status_message)
        let element_id = "download_all_" + download_params.di_id
        let files_to_return = await Download_Multiple(element_id, download_params.filename, download_params.downloadable_id, "Downloading All: ", download_params.di_id)
        let message: returnMessage = {
            message_type: MT.file,
            element_id: element_id,
            text: "Downloaded All",
            progress: 1,
            file_buffer: files_to_return.file,
            filename: download_params.filename + ".zip",
        }
        port.postMessage(message, [files_to_return.file])
        count += 1;
    }
}

async function Download_Multiple(clicked_element_id: string, filename: string, downloadable_id: string, orig_text: string, di_id: string): Promise<fileReturn> {

    let zip = new JSZip();

    let response = await fetch("/download/multi/" + di_id + "/" + downloadable_id + "/")
    let data = await response.json()
    let total_files = data.files_to_download.length
    let file_count = 0
    for (let file_info of data.files_to_download) {
        let file_params: downloadFileParameters = {
            element_id: "download_" + file_info.id,
            orig_text: file_info.filename,
            di_file_id: file_info.id,
            size: file_info.size,
            di_id: data.di_id,
            product_slug: data.product_slug
        }

        let file = await downloadPromise(file_params)
        zip.file(file_info.download_as, file.file)
        file_count += 1
        let message: returnMessage = {
            message_type: MT.progress,
            element_id: clicked_element_id,
            text: orig_text + " Downloading",
            progress: file_count / total_files
        }
        port.postMessage(message)
    }

    let zip_array = await zip.generateAsync({
        type: "arraybuffer",
        compression: "STORE",
        compressionOptions: {
            level: 1
        }
    }, function updateCallback(metadata) {
        let message: returnMessage = {
            message_type: MT.progress,
            element_id: clicked_element_id,
            text: orig_text + " Compressing",
            progress: metadata.percent / 100
        }
        port.postMessage(message)
    })
    return {
        file: zip_array,
        filename: 'Not used'
    }
}

async function Download(file: downloadFileParameters): Promise<fileReturn> {
    return await downloadPromise(file, true);
}

//element_id: string, product_slug: string, di_id: number, di_file_id: number, total_size: number
function downloadPromise(parameters: downloadFileParameters, single = false): Promise<fileReturn> {
    return new Promise<fileReturn>(function (resolve, reject) {
        let message: returnMessage = {
            message_type: MT.progress,
            element_id: parameters.element_id,
            text: parameters.orig_text + " Downloading",
            progress: 0
        }
        port.postMessage(message)

        let requestURL = "/download/" + parameters.di_id + "/" + parameters.di_file_id + "/";

        let request = new XMLHttpRequest();
        request.open('GET', requestURL);
        request.responseType = 'json';
        request.send();


        const attempt_download = function (server_file_response: serverFileResponse, attempt = 1, primary_source_blocked?: boolean): Promise<Response> {
            let primary_file_source = server_file_response.seed1;
            let secondary_file_source = server_file_response.seed2;

            let source = primary_file_source
            if (primary_source_blocked) {
                source = secondary_file_source
            }
            return fetch(source)
                .then(async response => { //https://github.com/AnthumChris/fetch-progress-indicators/blob/master/fetch-basic/supported-browser.js
                    if (!response.ok) {
                        if (attempt > 3) {
                            let message: returnMessage = {
                                message_type: MT.error,
                                element_id: parameters.element_id,
                                text: parameters.orig_text + " " + response.status + " Error! Please refresh and retry.",
                            }
                            port.postMessage(message)
                            throw Error(response.status + ' ' + response.statusText)
                        } else {
                            if (!primary_source_blocked) {
                                primary_source_blocked = true;
                            }
                            await attempt_download(server_file_response, attempt + 1, primary_source_blocked)
                        }
                    }
                    if (!response.body) {
                        throw Error('ReadableStream not yet supported in this browser.')
                    }
                    let loaded = 0;

                    return new Response(
                        new ReadableStream({
                            start(controller) {
                                const reader = response.body.getReader();
                                read();

                                function read() {
                                    reader.read().then(({done, value}) => {
                                        if (done) {
                                            controller.close();
                                            return;
                                        }
                                        loaded += value.byteLength;
                                        let message: returnMessage = {
                                            message_type: MT.progress,
                                            element_id: parameters.element_id,
                                            text: parameters.orig_text + " Downloading",
                                            progress: loaded / parameters.size
                                        }
                                        port.postMessage(message)
                                        controller.enqueue(value);
                                        read();
                                    }).catch(error => {
                                        console.error(error);
                                        controller.error(error)
                                    })
                                }
                            }
                        })
                    );
                }).catch(function (error) {
                    if (attempt > 3) {
                        let message: returnMessage = {
                            message_type: MT.error,
                            element_id: parameters.element_id,
                            text: parameters.orig_text + " " + error + " Error! Please refresh and retry.",
                        }
                        port.postMessage(message)
                        throw Error(error)
                    } else {
                        return attempt_download(server_file_response, attempt + 1, primary_source_blocked)
                    }
                })
        }
        request.onload = function () {
            let response = request.response as serverFileResponse;
            let file_name = response.clean_name;
            let extension = file_name.substring(file_name.lastIndexOf('.') + 1).toLowerCase();
            let primary_file_source = response.seed1;
            let secondary_file_source = response.seed2;
            if (single && ((extension == "zip") || (extension == 'obj'))) {
                //|| !["zip", "obj"].includes(extension) removed because it opens images in new tabs, which we don't want.
                console.log(file_name)
                resolve({filename: file_name, url: primary_file_source})
                return //Download.js will get the rest of the file.
            }
            attempt_download(response, 1).then(res => res.blob())
                .then(blob => {
                        try {
                            return blob.arrayBuffer()
                        } catch (error) {
                            return new Promise<ArrayBuffer>((resolve) => {
                                let fr = new FileReader();
                                fr.onload = () => {
                                    resolve(fr.result as ArrayBuffer);
                                };
                                fr.readAsArrayBuffer(blob);
                            })
                        }

                    }
                )
                .then(ab => {
                        if (extension == "txt") {
                            let b = Buffer.concat([Buffer.from(ab), Buffer.from("\n" + request.response['comment_stamp'])])
                            let stamped_ab = b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength)
                            resolve({file: <ArrayBuffer>stamped_ab, filename: file_name})
                        } else {
                            resolve({file: ab, filename: file_name})
                        }
                    }
                )
        }
    })

}

function getPosition(string: string, subString: string, occurrence: number) {
    /**
     * @returns the position of the start of the nth occurrence of the substring in string
     */
    return string.split(subString, occurrence).join(subString).length;
}