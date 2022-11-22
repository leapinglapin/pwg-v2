import * as Dropzone from "dropzone";
import {getCookie} from "../support/cookies";

const csrftoken = getCookie('csrftoken');

function get_btn_id(name: string) {
    return "upload_image_" + name
}


export function configureImageUploadButtons() {
    let image_area = document.getElementById("product_image_gallery")

    document.querySelectorAll(".cgt_image_upload").forEach(function (upload_button: HTMLButtonElement) {
        console.log(upload_button)
        let myDropzone = new Dropzone(upload_button, {
            previewsContainer: false,
            createImageThumbnails: true,
            dictDefaultMessage: "Upload Images",
            parallelUploads: 2,
            maxFilesize: 2048,
            timeout: 0
        });

        myDropzone.on("addedfile", function (file: any) {
            const btn = document.createElement("BUTTON");   // Create a <button> element
            btn.classList.add('btn')
            btn.classList.add('btn-warning')

            const name = file.name;

            btn.innerHTML = "Uploading: " + name;
            btn.id = get_btn_id(name)
            image_area.append(btn)


        })

        myDropzone.on("sending", function (file: any, xhr: any, formData: any) {
            let name = file.name;
            // @ts-ignore
            if (file.fullPath) {
                // @ts-ignore
                name = file.fullPath
                formData.append('full_path', name)
            }
            console.log(formData)
            xhr.setRequestHeader('X-CSRFToken', csrftoken)

            const btn = document.getElementById(get_btn_id(name))

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

            const btn = document.getElementById(get_btn_id(name))
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
    });
}