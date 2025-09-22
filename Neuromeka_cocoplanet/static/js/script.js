function fetchStatus() {
    fetch("/api/status")
        .then(response => response.json())
        .then(data => {
            updateOrderStatus(data.order_status);
            updateProcessing(data.processing);
            renderPickup(data.pickup_list);
        })
        .catch(err => console.error("Error fetching status:", err));
}
function updateOrderStatus(orderStatus) {
    const orderStatusList = document.getElementById("order-status-list");
    orderStatusList.innerHTML = ""; // 초기화

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
        if (cell) {
            cell.innerHTML = ""; 
        }
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

document.addEventListener("DOMContentLoaded", () => {
    fetchStatus();
    setInterval(fetchStatus, 500); 

});
