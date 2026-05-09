import { Api } from "./client";

const apiBaseUrl = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

const api = new Api({
    baseURL: apiBaseUrl,
    securityWorker: (token) => {
        if (token) {
            return {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        }
        return {}
    }
})


export default api
