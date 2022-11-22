const mix = require("laravel-mix");

const output =
    process.env.TAILWIND_MODE == "watch" ? "../static/css" : "static/css";

console.log(output);

mix.setPublicPath(output);
mix.postCss("src/stylesheets/default.css", "default.css", [
    require("postcss-import"),
    require("tailwindcss")("src/configs/default.js"),
    require("autoprefixer"),
]);
