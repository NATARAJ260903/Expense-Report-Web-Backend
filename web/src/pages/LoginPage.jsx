import React,{useState} from "react";
import {login} from "../api";

const demoAccounts={
  employee:"amit@beeja.com",
  manager:"priya@beeja.com",
  finance_admin:"karan@beeja.com"
};

export default function LoginPage({onLogin}){
  const [email,setEmail]=useState(demoAccounts.employee);
  const [password,setPassword]=useState("");
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
      const d=await login(email.trim(),password,role);
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
    <label>Password</label>
    <input type="password" value={password} onChange={e=>setPassword(e.target.value)} required minLength={6} autoComplete="current-password"/>
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
      Employee: amit@beeja.com / employee123<br/>
      Manager: priya@beeja.com / manager123<br/>
      Finance: karan@beeja.com / finance123
    </div>
  </form></div>
}
