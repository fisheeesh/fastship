import { createContext, useEffect, useState } from "react";
import { toast } from "sonner";
import api from "~/lib/api";

interface AuthContextType {
    token: string | null
    login: (email: string, password: string) => Promise<void>
    logout: () => void
}

const AuthContext = createContext<AuthContextType>({
    token: null,
    login: async () => { },
    logout: () => { }
})

function AuthProvider({ children }: { children: React.ReactNode }) {
    const [token, setToken] = useState<string | null>(null)

    // ? check whether user is already login or not
    useEffect(() => {
        const token = localStorage.getItem("token")

        if (token) {
            setToken(token)
            api.setSecurityData(token)
        }
    }, [])

    const login = async (email: string, password: string) => {
        try {
            const { data } = await api.seller.loginSeller({
                username: email,
                password
            })

            if (data?.access_token) {
                setToken(data.access_token)
                api.setSecurityData(data.access_token)
                // ? store in localStorage for persistence
                localStorage.setItem("token", data.access_token)

                toast.success("Success", {
                    description: "Successfully logged in."
                })
            }
        } catch (error) {
            console.log(error)
            toast.error("Error", {
                description: "Login faild. Please check your credentails."
            })

        }
    }

    const logout = async () => {
        await api.seller.logoutSeller()
        setToken(null)
        api.setSecurityData(null)
        // ? remove from localStorage after logout
        localStorage.removeItem("token")
    }

    return (
        <AuthContext.Provider value={{ token, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export { AuthProvider, AuthContext, type AuthContextType }