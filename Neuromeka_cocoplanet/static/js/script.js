function hasValidData(data) {
    return (
        (data.pickup_list && data.pickup_list.length > 0) ||
        (data.order_status && data.order_status.length > 0) ||
        (data.processing && data.processing.order_no && data.processing.order_no !== "-")
    );
}

function fetchStatus() {
    fetch("/api/status")
        .then(response => {
            if (!response.ok) throw new Error("서버 응답 없음");
            return response.json();
        })
        .then(data => {
            if (hasValidData(data)) {
                showMainUI();
                console.log(data);
                updateOrderStatus(data.order_status);
                updateProcessing(data.processing);
                renderPickup(data.pickup_list);
            } else {
                // 데이터 없음 → 슬라이드쇼
                showSlideshow();
            }
        })
        .catch(err => {
            console.error("Error fetching status:", err);
            // 통신 실패 → 슬라이드쇼
            showSlideshow();
        });
}


function updateOrderStatus(orderStatus) {
    const orderStatusList = document.getElementById("order-status-list");
    orderStatusList.innerHTML = "";

    orderStatus.slice(0, 3).forEach(item => {
        const li = document.createElement("li");
        li.textContent = `#${item.order_no} - ${item.menu}`;
        orderStatusList.appendChild(li);
    });

    if (orderStatus.length > 3) {
        const li = document.createElement("li");
        li.textContent = "...";
        orderStatusList.appendChild(li);
    }
}

function updateProcessing(processing) {
    const processingEl = document.getElementById("processing");
    if (!processing || !processing.order_no || processing.order_no === "-") {
        processingEl.textContent = "";
    } else {
        processingEl.textContent = `#${processing.order_no} - ${processing.menu}`;
    }
}

function renderPickup(pickupList) {
    for (let i = 1; i <= 16; i++) {
        const cell = document.getElementById(`pick-${i}`);
        if (cell) cell.innerHTML = "";
    }

    pickupList.forEach(item => {
        const cell = document.getElementById(`pick-${item.pick}`);
        if (cell) {
            cell.innerHTML = `
                <div class="pickup-card">
                    <img src="/static/images/ic_cup.png" alt="cup" class="pickup-icon">
                    <div class="pickup-text">
                        <div class="order-no">${item.order_no}</div>
                        <div class="menu">${item.menu}</div>
                    </div>
                </div>
            `;
        }
    });
}

// ===== UI 전환 =====
let currentView = "slideshow"; 

function showMainUI() {
    if (currentView === "main") return;
    currentView = "main";

    const slideshow = document.getElementById("slideshow");
    const mainUI = document.getElementById("main-ui");

    slideshow.style.transition = "opacity 1s ease-in-out";
    slideshow.style.opacity = 0;

    setTimeout(() => {
        slideshow.style.display = "none";
        mainUI.style.display = "block";
        mainUI.style.opacity = 0;

        setTimeout(() => {
            mainUI.style.transition = "opacity 1.5s ease-in-out";
            mainUI.style.opacity = 1;
        }, 50);
    }, 1000);
}

function showSlideshow() {
    if (currentView === "slideshow") return;
    currentView = "slideshow";

    const slideshow = document.getElementById("slideshow");
    const mainUI = document.getElementById("main-ui");

    mainUI.style.transition = "opacity 1s ease-in-out";
    mainUI.style.opacity = 0;

    setTimeout(() => {
        mainUI.style.display = "none";
        slideshow.style.display = "block";
        slideshow.style.opacity = 0;

        setTimeout(() => {
            slideshow.style.transition = "opacity 1.5s ease-in-out";
            slideshow.style.opacity = 1;
        }, 50);
    }, 1000);
}

// ===== 슬라이드쇼 순환 =====
function startSlideshow() {
    let slides = document.querySelectorAll("#slideshow img");
    let current = 0;

    function showSlide() {
        slides[current].classList.remove("active");
        current = (current + 1) % slides.length;
        slides[current].classList.add("active");
    }
    setInterval(showSlide, 4000);
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("main-ui").style.display = "none"; //
    startSlideshow();

    fetchStatus();
    setInterval(fetchStatus, 1000);
});
