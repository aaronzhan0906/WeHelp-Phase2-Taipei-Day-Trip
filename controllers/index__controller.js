import { fetchAttractionsData } from "../views/index__view--attractions.js";
import { listBarApi } from "../views/index__view--listbar.js";
import { searchInputApi } from "../views/index__view--search.js";

// utils //
import { getUserDomElements, setupEventListeners } from "../utils/user__dom.js"
import { detectJwt } from "../utils/user__auth.js"
import { initial } from "../utils/initial.js"


window.addEventListener("DOMContentLoaded", () => {
    // attractions //
    fetchAttractionsData();
    listBarApi();
    searchInputApi();

    // user //
    const elements = getUserDomElements();
    setupEventListeners(elements);
    detectJwt(elements)

    // booking //
    initial()
});




