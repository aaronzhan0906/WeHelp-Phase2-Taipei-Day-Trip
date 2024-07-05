export const setupTapPay = (tripDetail) => {
    TPDirect.card.setup({
        fields: {
            number: {
                element: "#card-number",
                placeholder: "**** **** **** ****"
            },
            expirationDate: {
                element: document.getElementById("card-expiration-date"),
                placeholder: "MM / YY"
            },
            ccv: {
                element: "#card-ccv",
                placeholder: "ccv"
            }
        },
        styles: {
            ":focus": {
                "color": "black"
            },
            ".valid": {
                "color": "green"
            },
            ".invalid": {
                "color": "red"
            },
            "@media screen and (max-width: 400px)": {
                "input": {
                    "color": "orange"
                }
            }
        },
        isMaskCreditCardNumber: true,
        maskCreditCardNumberRange: {
            beginIndex: 6,
            endIndex: 11
        }
    });


    TPDirect.card.onUpdate(function (update) {
        if (update.canGetPrime) {
            // Enable submit button to get prime
            document.querySelector(".confirm__submit").removeAttribute("disabled");
        } else {
            // Disable submit button to get prime
            document.querySelector(".confirm__submit").setAttribute("disabled", true);
        }

        // Handle card type 
        if (update.cardType) {
            switch (update.cardType) {
                case "visa":
                    TPDirect.ccv.setupCardType(TPDirect.CardType.VISA);
                    break;
                case "jcb":
                    TPDirect.ccv.setupCardType(TPDirect.CardType.JCB);
                    break;
                case "mastercard":
                    TPDirect.ccv.setupCardType(TPDirect.CardType.MASTERCARD);
                    break;
            }
         }

        // Handle field status
        ["number", "expiry", "ccv"].forEach(field => {
            const element = document.querySelector(`#card-${field}`);
            if (update.status[field] === 2) {
                element.classList.add("invalid");
                element.classList.remove("valid");
            } else if (update.status[field] === 0) {
                element.classList.add("valid");
                element.classList.remove("invalid");
            } else {
                element.classList.remove("valid", "invalid");
            }
        });
    });

    const confirmButton = document.querySelector(".confirm__submit");
    confirmButton.addEventListener("click", (event) => onSubmit(event, tripDetail));
};


const validateContactInfo = () => {
    const nameElement = document.querySelector(".contact__form--name");
    const emailElement = document.querySelector(".contact__form--email");
    const phoneElement = document.querySelector(".contact__form--telephone");

    const name = nameElement ? nameElement.value.trim() : "";
    const email = emailElement ? emailElement.value.trim() : "";
    const phone = phoneElement ? phoneElement.value.trim() : "";

    if (!name){
        alert("請輸入名字")
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if(!email || !emailPattern.test(email)){
        alert("請輸入有效的電子郵件");
        return false;
    }

    const phonePattern = /^[0-9]{10}$/;
    if(!phone || !phonePattern.test(phone)) {
        alert("請輸入有效的電話號碼");
        return false;
    }

    return { name, email, phone };
}


const onSubmit = (event, tripDetail) =>  {
    event.preventDefault();

    const tappayStatus = TPDirect.card.getTappayFieldsStatus();
    const contactInfo = validateContactInfo();
    if (!contactInfo) {
        return;
    }

    if (tappayStatus.canGetPrime === false) {
        console.log("無法取得 Prime，請檢查信用卡資訊是否正確");
        return;
    }

    TPDirect.card.getPrime((result) => {
        if (result.status !== 0) {
            alert("取得 Prime 失敗: " + result.msg);
            return;
        }

        const prime = result.card.prime;        
        const orderData = {
            prime: prime,
            order: {
                price: tripDetail.price,
                trip: tripDetail.attraction,
                date: tripDetail.date,
                time: tripDetail.time,
                contact: contactInfo
            },
        };
        console.log(orderData)
        sendPaymentToServer(orderData);
    });
}

async function sendPaymentToServer(orderData) {
    try {
        const response = await fetch("/api/orders", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `${localStorage.getItem("jwt")}`
            },
            body: JSON.stringify(orderData),
        });
        
        const newToken = response.headers.get("Authorization")
        if (newToken) localStorage.setItem("jwt", newToken);
        const paymentData = await response.json();
        const order_number = paymentData.data.number

        if (paymentData.data.payment.status === 0) {
            window.location.href = `/thankyou?number=${order_number}`
        } else {
            alert(`付款失敗，訂單編號 ${order_number}`)
        }
    } catch (error) {
        console.error("支付請求錯誤：", error);
        alert("發生錯誤，請稍後再試");
    }
}
