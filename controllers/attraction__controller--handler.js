// time and charge option // 
export const attractionHandler = () =>{
    timeAndCharge();
    dateHandler();
    bookingInAttractionPage();
}

export const timeAndCharge = () => {
    const timeOptions = document.querySelectorAll(".booking__time--radio")
    const costAmount = document.querySelector(".booking__cost--amount")

    timeOptions[0].checked = true;
    costAmount.textContent = " 2000 ";

    timeOptions.forEach(option => {
        option.addEventListener("change", () => {
            const selectedTime = document.querySelector(".booking__time--radio:checked")?.nextElementSibling?.textContent;
            costAmount.textContent = selectedTime === "上半天" ? "2000" : "2500";
        });
    });
};

export const dateHandler = () => {
    const dateSelector = document.querySelector(".booking__date--selector");
    
    if (dateSelector) {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      
      const formattedDate = tomorrow.toISOString().split("T")[0];
      
      dateSelector.min = formattedDate;
    
      dateSelector.addEventListener('focus', function() {
        this.placeholder = "";
      });
    }
};

// submit booking data by hitting button in attraction page// 
export const bookingInAttractionPage = () => {
    const bookingForm = document.querySelector(".section__booking");
    const getJWT = localStorage.getItem("jwt")
    
    if (bookingForm) {
      bookingForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        if (!getJWT) {
            alert("請登入後再預定行程");
            return;
        }

        const formData = new FormData(event.target);
        
        const path = window.location.pathname;
        const parts = path.split('/');
        const attractionId = parts[parts.length - 1];
        
        const date = formData.get("date");
        const timeRadios = formData.getAll("time");
        let time = "morning"; 
        if (timeRadios.includes("afternoon")) {
            time = "afternoon";
        }

        if (!date) {
          alert("請選擇日期");
          return;
        }
        
        const data = {
          attractionId: attractionId,
          date: date,
          time: time,
          price: parseInt(document.querySelector(".booking__cost--amount").textContent, 10)
        };

        console.log(data)
        
        try {
          const response = await fetch("/api/booking", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${localStorage.getItem("jwt")}`
            },
            body: JSON.stringify(data)
          });
          
          if (response.ok) {
            const newToken = response.headers.get("Authorization");
            if (newToken) {
              localStorage.setItem("jwt", newToken.split(" ")[1]);
            }
            window.location.href = "/booking";
            alert("預定成功");
          } else {
            const errorData = await response.json();
            alert(`預定失敗: ${errorData.message || '未知錯誤'}`);
          }
        } catch (error) {
          console.error("預定過程中發生錯誤:", error);
          alert("預定失敗，請稍後再試");
        }
      });
    } else {
      console.error("Booking form not found");
    }
  };