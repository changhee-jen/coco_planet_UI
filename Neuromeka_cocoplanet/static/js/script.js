function hasValidData(data) {
    return (
        (data.pickup_list && data.pickup_list.length > 0) ||
        (data.order_status && data.order_status.length > 0) ||
        (data.processing && data.processing.order_no && data.processing.order_no !== "-")
    );
}

let slideshowTimer = null;
let slideshowDelayTimer = null;
let currentView = "slideshow";

function fetchStatus() {
    fetch("/api/status")
        .then(response => {
            if (!response.ok) throw new Error("서버 응답 없음");
            return response.json();
        })
        .then(data => {
            if (hasValidData(data)) {
                showMainUI(); 
                updateOrderStatus(data.order_status);
                updateProcessing(data.processing);
                renderPickup(data.pickup_list);
            } else {
                showSlideshow();
            }
        })
        .catch(err => {
            console.error("Error fetching status:", err);
            showSlideshow();
        });
}

function updateProcessing(processingList) {
    const container = document.getElementById("processing-content");
    container.innerHTML = "";

    if (!processingList || processingList.length === 0) {
        return;
    }


    processingList.slice(0, 2).forEach(proc => {
        const wrapper = document.createElement("div");
        wrapper.classList.add("processing-container");
    if (!processingList || processingList.length === 0) {
            container.style.display = "none";
            return;
        }
        wrapper.innerHTML = `
            <div class="processing-title" style="margin-top:15px;">#${proc.order_no} - ${proc.menu}</div>
            <div class="progress-container">
                <div id="progress-icon-container">
                    <img id="progress-icon" src="/static/images/${proc.progress >= 100 ? "ic_completed.png" : "loading.gif"}" 
                         alt="progress">
                </div>
                <div class="progress-text-container">
                    <div id="progress-info">
                        <span id="progress-text">${proc.progress}%</span>
                        <span id="progress-status">${proc.progress >= 100 ? "Completed" : "Brewing"}</span>
                    </div>
                    <div id="progress-bar-container">
                        <div id="progress-bar" class="progress-bar" style="width:${proc.progress}%;"></div>
                    </div>
                </div>
            </div>
        `;

        container.appendChild(wrapper);
    });
}


// ===== Order Status =====
function updateOrderStatus(orderStatus) {
    const orderStatusList = document.getElementById("order-status-list");
    orderStatusList.innerHTML = "";

    orderStatus.slice(0, 5).forEach(item => {
        const li = document.createElement("li");
        li.textContent = `#${item.order_no} - ${item.menu}`;
        orderStatusList.appendChild(li);
    });

    if (orderStatus.length > 5) {
        const li = document.createElement("li");
        li.textContent = "...";
        orderStatusList.appendChild(li);
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
function showMainUI() {
    if (currentView === "main") return;
    currentView = "main";

    stopSlideshow();

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

function showTempMainThenSlideshow() {
    if (currentView === "slideshow") return;
    currentView = "temp-main";

    stopSlideshow();

    const slideshow = document.getElementById("slideshow");
    const mainUI = document.getElementById("main-ui");

    slideshow.style.display = "none";
    mainUI.style.display = "block";
    mainUI.style.opacity = 1;

    slideshowDelayTimer = setTimeout(() => {
        showSlideshow();
    }, 3000);
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
            slideshow.style.transition = "opacity 1s ease-in-out";
            slideshow.style.opacity = 1;
            startSlideshow();
        }, 50);
    }, 1000);
}

// ===== 슬라이드쇼 =====
function resetVideo(videoEl) {
    if (!videoEl) return;
    videoEl.pause();
   // videoEl.currentTime = 0;  
}


function startSlideshow() {
    let slides = document.querySelectorAll("#slideshow img, #slideshow video");
    let current = 0;

    function showSlide() {
        slides[current].classList.remove("active");
        if (slides[current].tagName === "VIDEO") {
            resetVideo(slides[current]);
            slides[current].removeEventListener("ended", onVideoEnd); // 이벤트 정리
        }

        current = (current + 1) % slides.length;
        slides[current].classList.add("active");

        if (slides[current].tagName === "VIDEO") {
            slides[current].play();
            slides[current].addEventListener("ended", onVideoEnd);
        } else {
            slideshowTimer = setTimeout(showSlide, 3000);
        }
    }

    function onVideoEnd() {
        showSlide(); // 영상이 끝나자마자 바로 전환
    }

    // 첫 시작
    slides[current].classList.add("active");
    if (slides[current].tagName === "VIDEO") {
        slides[current].play();
        slides[current].addEventListener("ended", onVideoEnd);
    } else {
        slideshowTimer = setTimeout(showSlide, 3000);
    }
}


function stopSlideshow() {
    if (slideshowTimer) {
        clearTimeout(slideshowTimer);
        slideshowTimer = null;
    }
    if (slideshowDelayTimer) {
        clearTimeout(slideshowDelayTimer);
        slideshowDelayTimer = null;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("main-ui").style.display = "none";
    document.getElementById("slideshow").style.display = "block"; 
    startSlideshow();

    fetchStatus();
    setInterval(fetchStatus, 1000);
});
