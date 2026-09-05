// Load dashboard data when the page opens
document.addEventListener("DOMContentLoaded", loadDashboard);


// ---------------------------------------------
// LOAD DASHBOARD
// ---------------------------------------------

async function loadDashboard() {
    try {
        const response = await fetch("/api/summary");

        if (!response.ok) {
            throw new Error("Failed to load dashboard data");
        }

        const data = await response.json();

        updateKPIs(data);
        updateStockOutTable(data.stock_out_risk);
        updateOverstockTable(data.overstock);
        updateTopProductsTable(data.top_products);
        updateStoreTable(data.store_sales);
        updateNonMoving(data.non_moving);

    } catch (error) {
        console.error(error);
    }
}


// ---------------------------------------------
// KPI CARDS
// ---------------------------------------------

function updateKPIs(data) {

    document.getElementById("totalRevenue").textContent =
        formatCurrency(data.total_revenue);

    document.getElementById("totalUnits").textContent =
        formatNumber(data.total_units);

    document.getElementById("totalStock").textContent =
        formatNumber(data.total_stock);

    document.getElementById("stockOutRisks").textContent =
        formatNumber(data.stock_out_risk.length);
}


// ---------------------------------------------
// STOCK-OUT TABLE
// ---------------------------------------------

function updateStockOutTable(items) {

    const table = document.getElementById("stockOutTable");

    table.innerHTML = "";

    items.slice(0, 10).forEach(item => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${item.product_name}</td>
            <td>${item.current_stock}</td>
            <td>${formatDays(item.days_of_stock)}</td>
        `;

        table.appendChild(row);
    });

    if (items.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="3">No stock-out risks detected.</td>
            </tr>
        `;
    }
}


// ---------------------------------------------
// OVERSTOCK TABLE
// ---------------------------------------------

function updateOverstockTable(items) {

    const table = document.getElementById("overstockTable");

    table.innerHTML = "";

    items.slice(0, 10).forEach(item => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${item.product_name}</td>
            <td>${item.current_stock}</td>
            <td>${formatDays(item.days_of_stock)}</td>
        `;

        table.appendChild(row);
    });

    if (items.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="3">No overstock detected.</td>
            </tr>
        `;
    }
}


// ---------------------------------------------
// TOP PRODUCTS
// ---------------------------------------------

function updateTopProductsTable(items) {

    const table = document.getElementById("topProductsTable");

    table.innerHTML = "";

    items.forEach(item => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${item.product_name}</td>
            <td>${item.category}</td>
            <td>${formatNumber(item.quantity_sold)}</td>
            <td>${formatCurrency(item.revenue)}</td>
        `;

        table.appendChild(row);
    });
}


// ---------------------------------------------
// STORE PERFORMANCE
// ---------------------------------------------

function updateStoreTable(items) {

    const table = document.getElementById("storeTable");

    table.innerHTML = "";

    items.forEach(item => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${item.store_name}</td>
            <td>${item.location}</td>
            <td>${formatNumber(item.quantity_sold)}</td>
            <td>${formatCurrency(item.revenue)}</td>
        `;

        table.appendChild(row);
    });
}


// ---------------------------------------------
// NON-MOVING INVENTORY
// ---------------------------------------------

function updateNonMoving(items) {

    const container = document.getElementById("nonMovingList");

    container.innerHTML = "";

    if (items.length === 0) {

        container.innerHTML =
            "<p>No non-moving inventory detected.</p>";

        return;
    }

    items.forEach(item => {

        const element = document.createElement("div");

        element.className = "non-moving-item";

        element.textContent =
            `${item.product_name} — ${item.current_stock} units`;

        container.appendChild(element);
    });
}


// ---------------------------------------------
// ASK GEMINI
// ---------------------------------------------

async function askQuestion() {

    const input =
        document.getElementById("questionInput");

    const answer =
        document.getElementById("chatAnswer");

    const question = input.value.trim();

    if (!question) {

        answer.textContent =
            "Please enter a question.";

        return;
    }

    answer.textContent =
        "Analyzing your sales and inventory data...";

    try {

        const response = await fetch(
            "/api/chat",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.answer || "Request failed"
            );
        }

        answer.textContent = data.answer;

    } catch (error) {

        console.error(error);

        answer.textContent =
            "Sorry, I could not process your question.";
    }
}


// ---------------------------------------------
// ENTER KEY SUPPORT
// ---------------------------------------------

document
    .getElementById("questionInput")
    .addEventListener("keydown", function(event) {

        if (event.key === "Enter") {
            askQuestion();
        }

    });


// ---------------------------------------------
// FORMATTING HELPERS
// ---------------------------------------------

function formatCurrency(value) {

    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }
    ).format(value);
}


function formatNumber(value) {

    return new Intl.NumberFormat(
        "en-IN"
    ).format(value);
}


function formatDays(value) {

    if (value >= 999) {
        return "No sales";
    }

    return `${value.toFixed(1)} days`;
}