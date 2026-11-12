import {renderPrice, installPriceHints} from "./price-hints.js";

installPriceHints();

setupLanguage(() => { document.title = document.querySelector('h1').textContent + ' · ' + document.querySelector('.eyebrow .effort').textContent + ' — ' + t('No SVG delivered'); });
