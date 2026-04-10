import axios from 'axios';
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api/v1';
export default axios.create({
    baseURL: BASE_URL,
    withCredentials: true
});
export const axiosPrivate = axios.create({
    baseURL: BASE_URL,
    headers: { 'Content-Type': 'multipart/form-data' },
    withCredentials: true
});
