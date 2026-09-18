import React,{useState} from "react";
import LoginPage from "./pages/LoginPage";
import ManagerPage from "./pages/ManagerPage";
import FinancePage from "./pages/FinancePage";
import EmployeePage from "./pages/EmployeePage";

export default function App(){
  const [user,setUser]=useState(()=>{const x=localStorage.getItem("user");return x?JSON.parse(x):null});
  if(!user) return <LoginPage onLogin={setUser}/>;
  const logout=()=>{localStorage.clear();setUser(null)};
  return <div className="app">
    <header className="topbar"><div><h1>Expense Report Management</h1><span>{user.name} · {user.role}</span></div><button onClick={logout}>Logout</button></header>
    <main>
      {user.role==="manager" && <ManagerPage/>}
      {user.role==="finance_admin" && <FinancePage/>}
      {user.role==="employee" && <EmployeePage/>}
    </main>
  </div>
}
