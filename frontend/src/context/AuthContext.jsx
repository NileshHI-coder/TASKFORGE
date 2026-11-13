import { createContext, useContext, useState } from 'react'
import api from '../services/api'
const AuthContext = createContext(null)
export function AuthProvider({ children }) {
 const [user, setUser] = useState(() => { try { return JSON.parse(localStorage.getItem('taskforge_user')) } catch { return null } })
 const login = async (email, password) => { const { data } = await api.post('/auth/login', { email, password }); localStorage.setItem('taskforge_token', data.token); localStorage.setItem('taskforge_user', JSON.stringify(data.user)); setUser(data.user) }
 const register = async (name, email, password) => { const { data } = await api.post('/auth/register', { name, email, password }); localStorage.setItem('taskforge_token', data.token); localStorage.setItem('taskforge_user', JSON.stringify(data.user)); setUser(data.user) }
 const logout = () => { localStorage.removeItem('taskforge_token'); localStorage.removeItem('taskforge_user'); setUser(null) }
 return <AuthContext.Provider value={{ user, login, register, logout }}>{children}</AuthContext.Provider>
}
export const useAuth = () => useContext(AuthContext)
