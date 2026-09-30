import { summary } from "../api/dashboard.js";
import { number } from "../utils/formatters.js";

function renderBars(selector, rows) {
    const root = document.querySelector(selector);
    if (!root) return;

    if (!rows?.length) {
        root.innerHTML = '<p class="muted">No data available.</p>';
        return;
    }

    const max = Math.max(...rows.map((row) => row.count), 1);
    root.innerHTML = rows.map((row) => {
        const width = Math.max((row.count / max) * 100, row.count ? 3 : 0);
        return `<div class="metric-row">
            <div class="metric-label"><span>${row.label}</span><strong>${number(row.count)}</strong></div>
            <div class="metric-track"><span style="width:${width}%"></span></div>
        </div>`;
    }).join("");
}

function renderLowStock(rows) {
    const body = document.querySelector("[data-low-stock]");
    if (!body) return;

    if (!rows?.length) {
        body.innerHTML = '<tr><td colspan="5" class="muted">No items are below reorder level.</td></tr>';
        return;
    }

    body.innerHTML = rows.map((row) => `<tr>
        <td>${row.item_code}</td>
        <td>${row.warehouse || "—"}</td>
        <td>${number(row.actual_qty)}</td>
        <td>${number(row.projected_qty)}</td>
        <td>${number(row.reorder_level)}</td>
    </tr>`).join("");
}

export async function render() {
    try {
        const data = await summary();
        const kpis = data.kpis || {};

        document.querySelector("[data-customer-count]").textContent = number(kpis.customers);
        document.querySelector("[data-product-count]").textContent = number(kpis.active_products);
        document.querySelector("[data-integration-count]").textContent = number(kpis.integration_logs);
        document.querySelector("[data-stock-count]").textContent = number(kpis.stock_requests);
        document.querySelector("[data-low-stock-count]").textContent = number(kpis.low_stock_items);
        document.querySelector("[data-dashboard-as-of]").textContent = data.as_of || "—";

        renderBars("[data-customer-status]", data.customer_status);
        renderBars("[data-request-status]", data.stock_request_status);
        renderBars("[data-integration-status]", data.integration_status);
        renderLowStock(data.low_stock);
    } catch (error) {
        document.querySelector("[data-dashboard]").insertAdjacentHTML(
            "afterbegin",
            '<div class="alert error">' + error.message + "</div>"
        );
    }
}
