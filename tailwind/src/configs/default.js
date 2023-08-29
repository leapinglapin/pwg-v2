const defaultTheme = require("tailwindcss/defaultTheme");

const primary = {
    "50": "#FAF6FE",
    "100": "#F1E7FB",
    "200": "#E3D0F7",
    "300": "#DBC2F5",
    "400": "#CFAFF2",
    "500": "#C49CEF",
    "600": "#B684EB",
    "700": "#A96EE7",
    "800": "#9A54E3", // 800 is the darkest we currently use
    "900": "#9A54E3",
    //https://coolors.co/gradient-maker/ffffff-faf6fe-f1e7fb-e3d0f7-dbc2f5-cfaff2-c49cef-b684eb-a96ee7-9a54e3?position=0,5,10,20,30,40,50,60,70,80&opacity=100,100,100,100,100,100,100,100,100,100&type=linear&rotation=90
};
module.exports = {
    content: ["../**/*.{html,tsx}"],
    theme: {
        // screens: {
        //   tw: "0px",
        //   ...defaultTheme.screens,
        // },
        extend: {
            colors: {
                primary: primary,
                neutral_back: {
                    DEFAULT: "#F5F5F5",
                    mid: "#343A40",
                    dark: "#1C211E",
                },
            },
            typography: {
                DEFAULT: {
                    css: {
                        lineHeight: "1.4",
                    },
                },
            },
            maxHeight: {
                "70-screen": "70vh",
            },
            outline: {
                "primary-500": primary["500"],
            },
        },
    },
    plugins: [
        require("@tailwindcss/forms"),
        require("@tailwindcss/typography"),
        require("@tailwindcss/line-clamp"),
    ],
    corePlugins: {
        preflight: false,
    },
    important: true,
};
