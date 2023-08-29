const defaultTheme = require("tailwindcss/defaultTheme");

const primary = {
    "50": "#fcfbf9",
    "100": "#fbf0df",
    "200": "#f6d5bd",
    "300": "#eaaa8d",
    "400": "#e17b5e",
    "500": "#ce583c",
    "600": "#b33e27",
    "700": "#8c2e1f",
    "800": "#622016",
    "900": "#3d140d",
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
                    mid: "#6c757d",
                    dark: "#2C2F33",
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
