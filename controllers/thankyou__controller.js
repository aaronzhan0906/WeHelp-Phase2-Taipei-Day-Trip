import { initial } from "../utils/initial.js"
import { getUserDomElements, setupEventListeners } from "../utils/user__dom.js"
import { detectJwt } from "../utils/user__auth.js"
import { thankyouView } from "../views/thankyou__view.js"


window.addEventListener("DOMContentLoaded",() => {
    // initial //
    initial();

    // utils //
    const elements = getUserDomElements();
    setupEventListeners(elements);
    detectJwt(elements);

    // thankyou__view //
    thankyouView()
});