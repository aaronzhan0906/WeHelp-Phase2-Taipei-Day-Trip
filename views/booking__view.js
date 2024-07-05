import { setupTapPay } from "../utils/tappay.js"

export const bookingView = () => {
    renderBookingPage()
    deleteBooking()
}

export const renderBookingPage = async () => {
    const storedJWT = localStorage.getItem("jwt");
    const journey = document.querySelector(".journey");
    const journeyGreet = document.querySelector(".journey__greet");
    const journeyGreetUsername = document.querySelector(".journey__greet--username");
    const signInName = localStorage.getItem("signInName");
    const deleteButton = document.querySelector(".journey__delete");


    if (!storedJWT) {
        const journeyGreetReply = document.createElement("div");
        journeyGreetReply.classList.add("journey__greet--reply");
        journeyGreet.appendChild(journeyGreetReply);
        journey.style.borderBottom = "none";
        journeyGreet.textContent ="請先登入後確認是否有待預定的行程"
        journeyGreet.style.display = "flex";
        journeyGreet.style.justifyContent = "center";
        journeyGreet.style.alignItems = "center";
        journeyGreet.style.height = "20vh";
        journeyGreet.style.margin = "0";
    } else {
        try {
            const response = await fetch("/api/booking", {
                headers: {
                    Authorization: `${localStorage.getItem("jwt")}`
                }
            });

            const journeyData = await response.json();

            if (journeyGreetUsername) {
                journeyGreetUsername.textContent = signInName;
            }

            if (journeyGreet) {
                journeyGreet.textContent = `您好，${signInName}，待預定的行程如下：`;
            }

            if (!journeyData.data) {
                const journeyGreetReply = document.createElement("div");
                journeyGreetReply.classList.add("journey__greet--reply");
                journeyGreet.appendChild(journeyGreetReply);
                journeyGreetReply.textContent = "目前沒有等待預定的行程";
                deleteButton.style.display = "none";    
                journey.style.borderBottom = "none";
            } else {
                const { attraction, date, time, price } = journeyData.data;
                const tripDetail = journeyData.data
                createBookingDOM(attraction, date, time, price);
                setupTapPay(tripDetail);
            }
        } catch (error) {
            console.error(error);
            const journeyGreetReply = document.createElement("div");
            journeyGreetReply.classList.add("journey__greet--reply");
            journeyGreet.appendChild(journeyGreetReply);
            journeyGreetReply.textContent = "獲取行程資料時發生錯誤，請稍後再試";
        }
    }
};


const createBookingDOM = (attraction, date, time, price) => {
    // turn to block //
    const journeySection = document.querySelector(".journey__section");
    const deleteButton = document.querySelector(".journey__delete");
    const contact = document.querySelector(".contact");
    const payment = document.querySelector(".payment");
    const confirm = document.querySelector(".confirm");

    journeySection.style.display = "flex";
    contact.style.display = "block";
    payment.style.display = "block";
    confirm.style.display = "block";
    deleteButton.style.display = "block";

    // variable //
    const sectionImage = document.querySelector(".section__image");
    const sectionAttractionVariable = document.querySelector(".section__attraction--variable");
    const sectionDateVariable = document.querySelector(".section__date--variable");
    const sectionTimeVariable = document.querySelector(".section__time--variable");
    const sectionCostVariable = document.querySelector(".section__cost--variable");
    const sectionAddressVariable = document.querySelector(".section__address--variable");
    const confirmCostVariable = document.querySelector(".confirm__cost--variable");

    sectionImage.style.backgroundImage = `url(${attraction.image})`;
    sectionAttractionVariable.textContent = attraction.name;
    sectionDateVariable.textContent = date;
    sectionCostVariable.textContent = price;
    sectionAddressVariable.textContent = attraction.address;
    confirmCostVariable.textContent = `新台幣 ${price} 元`

    if (time === "morning") {
        sectionTimeVariable.textContent = "早上 9 點 ～ 12 點";
    } else if (time === "afternoon") {
        sectionTimeVariable.textContent = "下午 1 點 ～ 5 點";
    }
};

export const deleteBooking = async () => {
    const journeySection = document.querySelector(".journey__section");
    const contact = document.querySelector(".contact");
    const payment = document.querySelector(".payment");
    const confirm = document.querySelector(".confirm");
    const deleteButton = document.querySelector(".journey__delete");
    deleteButton.addEventListener("click", async ()=> {
        try {
            const deleteRequest = await fetch("/api/booking", {
                method: "DELETE",
                headers: {
                    Authorization: `${localStorage.getItem("jwt")}`
                }
            });
            console.log(deleteRequest)

            if (deleteRequest.ok) {
                const noBookingToken = deleteRequest.headers.get("Authorization");
                localStorage.setItem("jwt", noBookingToken)
                journeySection.style.display = "none";
                contact.style.display = "none";
                payment.style.display = "none";
                confirm.style.display = "none";
                renderBookingPage();
            } 
        } catch (error) {
            console.error(`刪除失敗: ${error.message}`);
        }
    });
};

