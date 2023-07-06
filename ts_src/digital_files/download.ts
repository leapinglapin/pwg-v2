import {saveAs} from "file-saver-es";
import {downloadFileParameters, downloadProductParams, requestMessage, returnMessage} from "./interfaces"
import {MessageType as MT} from "./consts";

import {Download} from "./components/Download";


Object.assign(window, {
    Download
})

let $body: HTMLElement;

export function loadDownloads() {    // HTML elements
    $body = document.body;
    if (window.Worker) {
        let download_worker = new Worker("/static/js/download_engine.js");

        download_worker.onmessage = function (e) {
            let message = <returnMessage>e.data;

            if (message.element_id != null) {
                let element = document.getElementById(message.element_id)
                element.innerHTML = message.text;
                if (message.progress) {
                    element.innerHTML += " " + Math.round(message.progress * 100) + '%';
                }
            } else {
                console.log('Message received from worker:');
                console.log(message)
            }
            if (message.message_type != undefined) {
                let error = false;
                switch (message.message_type) {
                    case MT.error:
                        error = true;
                        console.log("Error in worker:" + message.element_id + " " + message.text)
                        break;
                    case MT.progress:
                        break;
                    case MT.download_status_update:
                        if (message.in_flight_downloads < 1) {
                            window.onbeforeunload = undefined;
                        }
                        break;
                    case MT.file:
                        try {
                            saveAs(new Blob([message.file_buffer]), message.filename)
                        } catch (e) {
                            console.log(e)
                            error = true
                        }
                        break;
                    case MT.url:
                        try {
                            console.log(message.filename)
                            //We do not want to use saveAs because the user doesn't get a progress bar
                            //saveAs(message.url, message.filename)
                            downloadUsingAnchorElement(message.url, message.filename)
                        } catch (e) {
                            console.log(e)
                            error = true
                        }
                        break;
                }
                if (error) {
                    let element = document.getElementById(message.element_id)
                    element.innerHTML = "There was an error, please refresh and try again or contact us"
                }
            }
        }
        document.querySelectorAll(".Download_Button").forEach(function (download_button: HTMLButtonElement) {
            let element_id = download_button.getAttribute("id")
            let product_slug = download_button.getAttribute("product_slug")
            let di_id = download_button.getAttribute("di_id");
            let downloadable_id = download_button.getAttribute("downloadable_id")
            let di_file_id = download_button.getAttribute("di_file_id");
            let size = parseInt(download_button.getAttribute("size"));
            download_button.addEventListener('click', function () {
                download_button.disabled = true;
                window.onbeforeunload = function () {
                    return "";
                }
                let orig_text = download_button.innerHTML
                let message: requestMessage = {
                    message_type: "Single",
                    downloadable_id: downloadable_id,
                    di_id: di_id,

                    files: [{element_id, product_slug, orig_text, di_id, di_file_id, size}]
                }
                download_worker.postMessage(message)
            });
        })
        document.querySelectorAll(".Download_All_Button").forEach(function (clicked_button: HTMLButtonElement) {
            let element_id = clicked_button.getAttribute("id")
            let download_as = clicked_button.getAttribute("download_as")
            let di_id = clicked_button.getAttribute("di_id");
            let downloadable_id = clicked_button.getAttribute("downloadable_id")
            let buttons = document.getElementsByClassName("di_id_" + di_id)
            let orig_text = clicked_button.innerHTML
            let files = getFilesInfo(buttons)
            clicked_button.addEventListener('click', function () {
                clicked_button.disabled = true;
                disableFilesForFolder(buttons)
                window.onbeforeunload = function () {
                    return "";
                }
                let message: requestMessage = {
                    message_type: "Multiple",
                    downloadable_id: downloadable_id,
                    di_id: di_id,
                    filename: download_as,
                    clicked_element_id: element_id,
                    orig_text: orig_text
                }
                download_worker.postMessage(message)
            });
        });

        document.querySelectorAll(".Download_Folder_Button").forEach(function (clicked_button: HTMLButtonElement) {
            let element_id = clicked_button.getAttribute("id")
            let folder_path = clicked_button.getAttribute("folder_path");
            let download_as = clicked_button.getAttribute("download_as")
            let di_id = clicked_button.getAttribute("di_id");
            let downloadable_id = clicked_button.getAttribute("downloadable_id")
            let orig_text = clicked_button.innerHTML
            let buttons = document.getElementsByClassName("download_recursive_" + folder_path)
            let files = getFilesInfo(buttons)
            clicked_button.addEventListener('click', function () {
                clicked_button.disabled = true;
                window.onbeforeunload = function () {
                    return "";
                }
                disableFilesForFolder(buttons)
                let message: requestMessage = {
                    message_type: "Multiple",
                    files: files,
                    downloadable_id: downloadable_id,
                    di_id: di_id,
                    filename: download_as,
                    clicked_element_id: element_id,
                    orig_text: orig_text
                }
                download_worker.postMessage(message)
            });
        });

        document.querySelectorAll(".Download_Pack_Button").forEach(function (clicked_button: HTMLButtonElement) {
            let element_id = clicked_button.getAttribute("id")
            let pack_id = clicked_button.getAttribute("pack_id")
            clicked_button.addEventListener('click', function () {
                QueuePackDownloads(download_worker, pack_id)
            });
        });
    }
}

async function QueuePackDownloads(download_worker: Worker, pack_id: string) {
    let response = await fetch("/packs/download/" + pack_id + "/")
    let data = await response.json()
    data.downloads.forEach(function (download_params: downloadProductParams) { //First disable all the buttons
        let buttons = document.getElementsByClassName("di_id_" + download_params.di_id)
        disableFilesForFolder(buttons)
    })
    window.onbeforeunload = function () {
        return "";
    }
    // Tell worker to download everything
    let message = {
        message_type: "Pack",
        orig_text: "Download Pack",
        clicked_element_id: "download_pack_" + pack_id,
        pack_id: pack_id,
        products: data.purchases,
    }
    download_worker.postMessage(message)
}


function getFilesInfo(buttons: HTMLCollectionOf<Element>): Array<downloadFileParameters> {
    let files: Array<downloadFileParameters> = []
    Array.prototype.forEach.call(buttons, function (download_button: HTMLButtonElement) {
        let element_id = download_button.getAttribute("id")
        let product_slug = download_button.getAttribute("product_slug")
        let orig_text = download_button.innerHTML
        let di_id = download_button.getAttribute("di_id");
        let di_file_id = download_button.getAttribute("di_file_id");
        let size = parseInt(download_button.getAttribute("size"));
        files.push({element_id, product_slug, orig_text, di_id, di_file_id, size})
    });
    return files
}

function disableFilesForFolder(buttons: HTMLCollectionOf<Element>) {
    Array.prototype.forEach.call(buttons, function (download_button: HTMLButtonElement) {
        download_button.disabled = true;
    });
    //TODO: get this function to disable the folder download buttons, and the individual download buttons.
}

function downloadUsingAnchorElement(url: string, filename: string) {
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.target = '_blank'
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
}