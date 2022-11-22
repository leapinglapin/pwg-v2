import * as Dropzone from "dropzone";
import {getCookie} from "../support/cookies";

const dz = Dropzone;
dz.autoDiscover = false;

interface uploadData {
    fd: FormData
    btn: HTMLElement
    name: string
}


const csrftoken = getCookie('csrftoken');

export function configUploadButtons() {
    SetRemoveButtons();

    // Load all these properties we need to submit to the correct urls
    let upload_info = document.getElementById("upload_info")
    let partner_slug = upload_info.getAttribute("partner_slug")
    let product_slug = upload_info.getAttribute("product_slug")
    let di_id = upload_info.getAttribute("di_id")
    let file_area = document.getElementById("files")
    document.querySelectorAll(".cgt_digital_upload").forEach(function (upload_button: HTMLButtonElement) {
        console.log(upload_button)
        let myDropzone = new Dropzone(upload_button, {
            previewsContainer: false,
            parallelUploads: 2,
            maxFilesize: 2048,
            timeout: 0
        });

        myDropzone.on("addedfile", function (file: any) {
            let btn = document.createElement("BUTTON");   // Create a <button> element
            btn.classList.add('btn')
            btn.classList.add('btn-warning')
            let name = file.name;
            // @ts-ignore
            if (file.fullPath) {
                // @ts-ignore
                name = file.fullPath
            }
            btn.innerHTML = "Uploading: " + name;
            btn.id = "uploading_" + name
            file_area.appendChild(btn)
            file_area.appendChild(document.createElement("br"))
        })

        myDropzone.on("sending", function (file: any, xhr: any, formData: any) {
            let name = file.name;
            // @ts-ignore
            if (file.fullPath) {
                // @ts-ignore
                name = file.fullPath
                formData.append('full_path', name)
            }
            let btn = document.getElementById("uploading_" + name)

            xhr.setRequestHeader('X-CSRFToken', csrftoken)

            xhr.upload.addEventListener("progress", function (evt: ProgressEvent<XMLHttpRequestEventTarget>) {
                if (evt.lengthComputable) {
                    console.log("add upload event-listener" + evt.loaded + "/" + evt.total);
                    btn.innerHTML = name + " " + evt.loaded + "/" + evt.total;

                }
            });
        })

        myDropzone.on("complete", function (file: any) {
            let xhr = file.xhr
            let name = file.name;
            // @ts-ignore
            if (file.fullPath) {
                // @ts-ignore
                name = file.fullPath
            }
            let btn = document.getElementById("uploading_" + name)
            console.log(file.xhr.status)
            if (xhr.status == 200) {
                btn.innerHTML = name + " Done!";
                btn.classList.remove('btn-warning')
                btn.classList.add('btn-success')
            } else {
                btn.innerHTML = name + " Something went wrong";
                btn.classList.remove('btn-warning')
                btn.classList.add('btn-danger')
            }
        })
    })
}

function SetRemoveButtons() {
    document.querySelectorAll(".Remove_Button").forEach(function (remove_button: HTMLElement) {
        let product_slug = remove_button.getAttribute("product_slug")
        let di_id = remove_button.getAttribute("di_id");
        let di_file_id = remove_button.getAttribute("di_file_id");
        remove_button.addEventListener('click', function () {
            Remove(product_slug, di_id, di_file_id)
        });
        console.log("Setting Remove button");
    })
    document.querySelectorAll(".RemoveFolderButton").forEach(function (remove_button: HTMLElement) {
        let product_slug = remove_button.getAttribute("product_slug")
        let di_id = remove_button.getAttribute("di_id");
        let downloadable_id = remove_button.getAttribute("downloadable_id");
        remove_button.addEventListener('click', function () {
            RemoveFolder(product_slug, di_id, downloadable_id)
        });
        console.log("Setting Remove button");
    })
}

function Remove(product_slug: string, di_id: string, di_file_id: string) {
    let upload_info = document.getElementById("upload_info")
    let partner_slug = upload_info.getAttribute("partner_slug")
    console.log("Downloading File");
    let request = new Request(
            '/shop/manage/<partner_slug>/product/<product_slug>/digital/<di_id>/remove/<di_file_id>/'
                .replace("<partner_slug>", partner_slug)
                .replace("<product_slug>", product_slug)
                .replace("<di_id>", String(di_id))
                .replace("<di_file_id>", String(di_file_id)),
            {headers: {'X-CSRFToken': csrftoken}}
        )
    ;
    fetch(request, {
        method: 'POST',
        mode: 'same-origin', // Do not send CSRF token to another domain.
    }).then(function (response) {
            console.log(response.status)
            console.log("File removed")
            //Remove the element
            let element_to_remove = document.getElementById("remove_" + di_file_id);
            element_to_remove.parentNode.removeChild(element_to_remove);
            element_to_remove = document.getElementById("download_" + di_file_id);
            element_to_remove.parentNode.removeChild(element_to_remove);
        }
    )

}

function RemoveFolder(product_slug: string, di_id: string, downloadable_id: string) {
    let upload_info = document.getElementById("upload_info")
    let partner_slug = upload_info.getAttribute("partner_slug")
    console.log("Downloading File");
    let request = new Request(
            '/shop/manage/<partner_slug>/product/<product_slug>/digital/<di_id>/remove/multi/<downloadable_id>/'
                .replace("<partner_slug>", partner_slug)
                .replace("<product_slug>", product_slug)
                .replace("<di_id>", String(di_id))
                .replace("<downloadable_id>", String(downloadable_id)),
            {headers: {'X-CSRFToken': csrftoken}}
        )
    ;
    fetch(request, {
        method: 'POST',
        mode: 'same-origin', // Do not send CSRF token to another domain.
    }).then(function (response) {
            console.log(response.status)
            console.log("File removed")
            //Remove the element
            let element_to_remove = document.getElementById("remove_folder_" + downloadable_id);
            element_to_remove.parentNode.removeChild(element_to_remove);
        }
    )

}
