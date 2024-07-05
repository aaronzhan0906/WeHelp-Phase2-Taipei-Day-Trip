import { fetchAttractionIdData } from "../models/attraction__model.js"
import { renderAttractionPage  } from "../views/attraction__view.js"
import { attractionHandler } from "./attraction__controller--handler.js"
// utils // 
import { initial } from "../utils/initial.js"
import { getUserDomElements, setupEventListeners } from "../utils/user__dom.js"
import { detectJwt } from "../utils/user__auth.js"


window.addEventListener("DOMContentLoaded",() => {
    const attractionId = getIdFromUrl();
    fetchAttractionIdData(attractionId)
    .then(renderAttractionPage)
    .catch(error => console.error("(attractionId) Error fetching attraction data.", error));
    
    // handler //
    attractionHandler();

    // user // 
    const elements = getUserDomElements();
    setupEventListeners(elements);
    detectJwt(elements);

    // initial //
    initial()
});


// get attractionId
const getIdFromUrl = () => {
    const urlParts = window.location.href.split("/");
    return parseInt(urlParts[urlParts.length - 1], 10);
};



