export async function thankyouView() {
    const url = new URL(window.location.href);
    const orderNumber = url.searchParams.get("number");
    try {

        const response = await fetch(`/api/order/${orderNumber}`, {
            headers: {
                "Authorization": `${localStorage.getItem("jwt")}`
            }
        });

        const data = await response.json();
        const orderNumberFromServer = data.data.number
        const detailNumber = document.querySelector(".detail__number");
        detailNumber.textContent = orderNumberFromServer;

        if (!response.ok) {
            throw new Error(data.message);
        }

    } catch (error) {
        console.error("錯誤:", error.message);
        throw error;
    }
}