// Client for the example terminal backend: https://github.com/stripe/example-terminal-backend
import getCookie from "./components/get_cookie";

class POSClient {
    private base_url: string;

    constructor(base_url: string) {
        this.base_url = base_url;

    }

    createConnectionToken() {
        return this.doPost("stripe_terminal_connection_token/", "");
    }


    createPaymentIntent(amount: number, cart_id: number) {
        const json = JSON.stringify(
            {
                "amount": amount
            }
        );
        return this.doPost("stripe/", json, cart_id);
    }

    capturePaymentIntent(paymentIntentId: string, cart_id: number) {
        const json = JSON.stringify(
            {
                "id": paymentIntentId
            }
        );
        return this.doPost("capture/", json, cart_id);
    }

    payCash(amount: number, cart_id: number) {
        const json = JSON.stringify(
            {
                "amount": amount
            }
        );
        return this.doPost("cash/", json, cart_id);
    }

    async doPost(endpoint: string, body: string,  cart_id?: number) {
        let url = this.base_url + "/";

        if (cart_id) {
            url +=  cart_id + "/"
        }
        url += endpoint
        let response = await fetch(url, {
            method: "post",
            body: body,
            headers: {'X-CSRFToken': getCookie('csrftoken')}

        });

        if (response.ok) {
            return response.json();
        } else {
            let text = await response.text();
            throw new Error("Request Failed: " + text);
        }
    }
}

export default POSClient;