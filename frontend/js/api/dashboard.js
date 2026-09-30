import { api } from "./client.js";

export async function summary() {
    const response = await api.get("/api/method/business_suite.api.dashboard_api.get_dashboard_summary");
    return response.data;
}
