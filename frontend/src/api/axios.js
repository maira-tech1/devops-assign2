import axios from 'axios';

const BASE_URL = 'http://localhost:5000/api/v1';

export default axios.create({
    baseURL: BASE_URL,
    withCredentials: true  // ← ADD THIS
});

export const axiosPrivate = axios.create({
    baseURL: BASE_URL,
    headers: { 'Content-Type': 'multipart/form-data' },
    withCredentials: true
});