export interface iCheckoutForm {
    setSummary: (summary: string) => void;
}

export interface iPaymentMethod {
    cart_id: number
    success_action: () => void;
}