import api from "./api"


export async function login(username, password){

    const response = await api.post(
        "/auth/login/",
        {
            username,
            password
        }
    )

    localStorage.setItem(
        "access_token",
        response.data.access
    )

    localStorage.setItem(
        "refresh_token",
        response.data.refresh
    )

    return response.data
}



export async function register(data){

    const response = await api.post(
        "/auth/register/",
        data
    )

    return response.data
}



export function logout(){

    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")

}



export function isAuthenticated(){

    return !!localStorage.getItem("access_token")

}