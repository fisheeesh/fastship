import { createContext, useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { toast } from "sonner";
import api from "~/lib/api";

type UserType = "seller" | "partner"

interface AuthContextType {
    token?: string | null
    user?: UserType
    login: (user_type: UserType, email: string, password: string) => Promise<void>
    logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
    token: null,
    login: async () => { },
    logout: async () => { },
})

function AuthProvider({ children }: { children: React.ReactNode }) {
    const [token, setToken] = useState<string | null>()
    const [user, setUser] = useState<UserType>()
    const navigate = useNavigate()

    // ? check whether user is already login or not
    useEffect(() => {
        const token = localStorage.getItem("token")

        if (token) {
            setToken(token)
            setUser(localStorage.getItem("user") as UserType)
            api.setSecurityData(token)
        }
        else {
            setToken(null)
        }
    }, [])

    const login = async (user_type: UserType, email: string, password: string) => {
        try {
            const loginUser = user_type === 'seller' ? api.seller.loginSeller : api.partner.loginDeliveryPartner
            const { data } = await loginUser({
                username: email,
                password
            })

            if (data?.access_token) {
                setToken(data.access_token)
                setUser(user_type)
                api.setSecurityData(data.access_token)
                // ? store in localStorage for persistence
                localStorage.setItem("token", data.access_token)
                localStorage.setItem("user", user_type)

                toast.success("Success", {
                    description: "Successfully logged in."
                })
                navigate("/dashboard")
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
        setUser(undefined)
        api.setSecurityData(null)
        // ? remove from localStorage after logout
        localStorage.removeItem("token")
        localStorage.removeItem("user")
    }

    return (
        <AuthContext.Provider value={{ token, user, login, logout }}>
            {token === undefined ? <div>Loading...</div> : children}
        </AuthContext.Provider>
    )
}

export { AuthProvider, AuthContext, type AuthContextType, type UserType }