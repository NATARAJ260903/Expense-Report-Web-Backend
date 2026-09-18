import React,{useState} from "react";
import {login} from "../api";

const demoAccounts={
  employee:"amit@employee.com",
  manager:"manager@company.com",
  finance_admin:"finance@company.com"
};

export default function LoginPage({onLogin}){
  const [email,setEmail]=useState(demoAccounts.employee);
  const [role,setRole]=useState("employee");
  const [error,setError]=useState("");
  const [loading,setLoading]=useState(false);

  function changeRole(e){
    const next=e.target.value;
    setRole(next);
    setEmail(demoAccounts[next]);
    setError("");
  }

  async function submit(e){
    e.preventDefault();
    setError("");
    setLoading(true);
    try{
      const d=await login(email.trim(),role);
      onLogin(d.user);
    }catch(x){
      setError(x.message || "Login failed");
    }finally{
      setLoading(false);
    }
  }

  return <div className="login"><form className="card" onSubmit={submit}>
    <h1>Expense Reports</h1>
    <p>Sign in to manage your expense reports.</p>
    <label>Email</label>
    <input type="email" value={email} onChange={e=>setEmail(e.target.value)} required autoComplete="email"/>
    <label>Role</label>
    <select value={role} onChange={changeRole}>
      <option value="employee">Employee</option>
      <option value="manager">Manager</option>
      <option value="finance_admin">Finance Admin</option>
    </select>
    <button className="primary" type="submit" disabled={loading}>
      {loading ? "Logging in..." : "Login"}
    </button>
    {error&&<p className="error">{error}</p>}
    <div className="hint">
      <strong>Demo accounts</strong><br/>
      Employee: amit@employee.com<br/>
      Manager: manager@company.com<br/>
      Finance: finance@company.com
    </div>
  </form></div>
}
