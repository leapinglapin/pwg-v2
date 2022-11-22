import {TypedUseSelectorHook, useDispatch, useSelector} from "react-redux";
import cartReducer, {updateCart} from "./reducers/cartSlice";

import {configureStore, compose} from "@reduxjs/toolkit";


const store = configureStore({
    reducer: {
        cart: cartReducer,
    },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

export default store;

// go ahead and preload the state
store.dispatch(updateCart());
