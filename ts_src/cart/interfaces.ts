export interface IButtonStatus {
    text: string;
    enabled: boolean;
}

export interface IItem {
    id: number;
    partner: IPartner;
    product: IProduct
    price: number;
    type: string;
    default_price: number;
    backorders_enabled: boolean;
    is_preorder: boolean;
    is_pay_what_you_want: boolean;
    inventory: number;
    button_status: IButtonStatus;
}

export interface IRowProps {
    pos: boolean
    item: IItem
    key: number
    quantity: number
    open: boolean
    price: number
    status: string
    price_per_unit_override: number
    estimated_cost: number
    full: boolean
    show_status_col: boolean
    description: string
    discount_code_message: string
}

export interface ICart {
    loaded?: boolean;
    status: string;
    lines: IRowProps[];
    payment_partner: IPartner;
    open: boolean;
    id: number;
    subtotal: string;
    final_tax: string;
    final_total: string;
    estimated_tax: string;
    estimated_total: string;
    total_paid: string;
    cash_paid: string;
    owner_info?: string;
    show_status_col: boolean;
    discount_code: string;
    discount_code_message: string

}

export interface IProduct {
    slug: any;
    id: number;
    name: string;
}

export interface IPartner {
    name: string;
    slug: string;
}

export interface IPOSProps {
    active_cart?: ICart;
    open_carts?: [ICart];
    pay_in_store_carts?: [ICart];
    pickup_carts?: [ICart];
    url: string;
}
