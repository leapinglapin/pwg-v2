const mix = require("laravel-mix");

const output =
    process.env.TAILWIND_MODE == "watch" ? "../static/css" : "static/css";

console.log(output);

mix.setPublicPath(output);
mix.postCss("src/stylesheets/opencgat.css", "opencgat.css", [
    require("postcss-import"),
    require("tailwindcss")("src/configs/opencgat.js"),
    require("autoprefixer"),
]);


mix.postCss("src/stylesheets/valhalla.css", "valhalla.css", [
    require("postcss-import"),
    require("tailwindcss")("src/configs/valhalla.js"),
    require("autoprefixer"),
]);