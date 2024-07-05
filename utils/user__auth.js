// userFormSignIn
let isSignIn = true;

export const userFormSignIn = async (elements) => {
    const { userForm, user ,overlay,formResult, userBox } = elements;
    console.log("～～～ 嘗試登入 ～～～")
    const formData = new FormData(userForm);
    const data = {
        email: formData.get("email"),
        password: formData.get("password")
    };
    overlay.addEventListener("click", () => {
        initialSignIn(elements);
    })

    if (!data.email || !data.password) {
        formResult.textContent = "請輸入所有必填內容";
        formResult.style.margin = "0 auto";
        formResult.style.color = "red";
        formResult.style.padding = "0 0 12px 0";
        formResult.style.display = "inline-block";
        userBox.style.textAlign = "center";
        userBox.style.height = "299px";
        return;
    }

    detectJwt(elements);
    
    try {
        const response = await fetch("/api/user/auth", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data),
            credentials: "include" 
        });

        const responseData = await response.json();
        if (response.ok) {
            console.log(responseData.message);
            const jwt = response.headers.get("Authorization");
            localStorage.setItem("jwt",jwt);
            detectJwt(elements);
            user.style.display = "none";
            overlay.style.display = "none";
        } else {
            console.log(responseData.message);
            const userBox = document.querySelector(".user__box");
            const formResult = document.querySelector(".form__result");
            formResult.className = "form__result";
            formResult.textContent = "電子郵件或密碼錯誤";
            formResult.style.margin = "0 auto";
            formResult.style.color = "red";
            formResult.style.padding = "0 0 12px 0";
            formResult.style.display = "inline-block";
            userBox.style.textAlign = "center";
            userBox.style.height = "299px";

            clearFormFields(elements);
        }

        if (window.location.pathname === '/booking') {
            window.location.reload();
        } 
    } catch (error) {
        console.error("Error:", error);
    }
}

// confirm USER-INFO //
export const detectJwt = async (elements) => {
    const { navigationRightSignIn, navigationRightBooking, user, overlay } = elements;
    const storedJwt = localStorage.getItem("jwt");
  
    if (!storedJwt) {
        console.log("<<< No JWT in localStorage. >>>");
        setLoggedOutState();
        return;
    }
  
    try {
      const response = await fetch("/api/user/auth", {
        method: "GET",
        headers: {
          "Authorization": `${storedJwt}`
        },
        });
    
        const responseConfirmJwt = await response.json();
    
        if (response.ok && responseConfirmJwt.data) {
            setLoggedInState(responseConfirmJwt.data.name);
        } else {
            setLoggedOutState();
            console.log(`detectJwtError: ${responseConfirmJwt.message}`);
        }
    } catch (error) {
        console.error("Error:", error);
        setLoggedOutState();
    }
  
    function setLoggedInState(name) {
        localStorage.setItem("signInName", name);
        navigationRightSignIn.style.display = "block";
        navigationRightSignIn.textContent = "登出系統";
        navigationRightSignIn.onclick = () => userSignOut(elements);
        
        navigationRightBooking.onclick = () => {
            const bookingPage = `http://${window.location.host}/booking`;
            window.location.href = bookingPage;
        };
    }
  
    function setLoggedOutState() {
        navigationRightSignIn.style.display = "block";
        navigationRightSignIn.textContent = "登入/註冊";
        navigationRightBooking.onclick = () => {
            user.style.display = "block";
            overlay.style.display = "block";
        };
    }
};


// userSignOut //
export const userSignOut = async (elements) => {
    const { navigationRightSignIn, user, overlay } = elements;
    localStorage.removeItem("jwt");
    localStorage.removeItem("signInName");
    navigationRightSignIn.textContent = "登入/註冊";
    user.style.display = "none";
    overlay.style.display = "none";
    
    overlay.addEventListener("click", () => {
        initialSignUp(elements);
    })

    if (window.location.pathname === '/booking') {
        window.location.reload();
    } 


    navigationRightSignIn.addEventListener("click", () => {
        user.style.display = "block";
        overlay.style.display = "block";
    });

    clearFormFields(elements);
}


// userFormSignUp //
export const userFormSignUp = async (elements) => {
    const { userForm, userBox, formResult,user, overlay } = elements;
    console.log("＠＠＠ 嘗試註冊 ＠＠＠")

    const formData = new FormData(userForm);
    const data = {
        name: formData.get("name"),
        email: formData.get("email"),
        password: formData.get("password")
    };

    if (!data.name || !data.email || !data.password) {
        formResult.textContent = "請輸入所有必填內容";
        formResult.style.margin = "0 auto";
        formResult.style.color = "red";
        formResult.style.padding = "0 0 12px 0";
        formResult.style.display = "inline-block";
        userBox.style.textAlign = "center";
        userBox.style.height = "356px";
        return;
    }

    try {
        const response = await fetch("/api/user", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const responseData = await response.json();
            if (responseData.ok) {
               
                formResult.className = "form__result";
                formResult.textContent = "註冊成功，請登入系統";
                formResult.style.margin = "0 auto";
                formResult.style.color = "green";
                formResult.style.padding = "0 0 12px 0";
                formResult.style.display = "inline-block";
                userBox.style.textAlign = "center";
                userBox.style.height = "356px";
                user.style.display = "block";
                overlay.style.display = "block";

                console.log(responseData.message);
            } 
        } else {
            const responseData = await response.json();
            if (responseData.error) {
                const userBox = document.querySelector(".user__box");
                const formResult = document.querySelector(".form__result");
                formResult.className = "form__result";
                formResult.textContent = `${responseData.message}`;
                formResult.style.margin = "0 auto";
                formResult.style.color = "red";
                formResult.style.padding = "0 0 12px 0";
                formResult.style.display = "inline-block";
                userBox.style.textAlign = "center";
                userBox.style.height = "356px";
                user.style.display = "block";
                overlay.style.display = "block";
                console.log(responseData.message);
            }
        }
    } catch (error) {
        console.error("Error", error);
    }
}


export const clearFormFields = (elements) => {
    const { formName, formEmail, formPassword } = elements;

    formName.value = "";
    formEmail.value = "";
    formPassword.value = "";
};


export const initialSignUp = (elements) => {
    const { formResult, user, formFooterRegister, formFooterQuestion, formTitle, formName, userBox, formSubmit} = elements;
    user.style.top = "246px";
    user.style.height = "332px";
    userBox.style.height = "322px";
    formName.style.display = "block";
    formFooterQuestion.textContent = "已經有帳戶了？";
    formFooterRegister.textContent = "點此登入";
    formTitle.textContent = "註冊會員帳號";
    formSubmit.textContent = "註冊新帳戶";
    clearFormFields(elements);
    isSignIn = false;

    if (formResult.textContent) {
        formResult.textContent = "";
        formResult.style.display = "none";
    }
}

export const initialSignIn = (elements) => {
    const { formResult, user, formFooterRegister, formFooterQuestion, formTitle, formName, userBox, formSubmit} = elements;
    user.style.top = "217.5px";
    user.style.height = "275px";
    userBox.style.height = "265px";
    formName.style.display = "none";
    formFooterQuestion.textContent = "還沒有帳戶？";
    formFooterRegister.textContent = "點此註冊";
    formTitle.textContent = "登入會員帳號";
    formSubmit.textContent = "登入帳戶";
    clearFormFields(elements);
    isSignIn = true;
    

    if (formResult.textContent) {
        formResult.textContent = "";
        formResult.style.display = "none";
    }
}

