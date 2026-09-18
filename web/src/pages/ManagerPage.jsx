import React,{useEffect,useState} from "react";
import {apiFetch} from "../api";
export default function ManagerPage(){
  const [items,setItems]=useState([]),[error,setError]=useState(""),[comments,setComments]=useState({});
  async function load(){try{setItems(await apiFetch("/manager/expenses"));setError("")}catch(e){setError(e.message)}}
  useEffect(()=>{load()},[]);
  async function approve(id){try{await apiFetch(`/expenses/${id}/approve`,{method:"POST"});load()}catch(e){setError(e.message)}}
  async function reject(id){const c=(comments[id]||"").trim();if(!c)return setError("Rejection comment is required.");try{await apiFetch(`/expenses/${id}/reject`,{method:"POST",body:JSON.stringify({comment:c})});load()}catch(e){setError(e.message)}}
  return <section><div className="page-head"><div><h2>Manager Pending Approvals</h2><p>Submitted expenses from your team.</p></div><button onClick={load}>Refresh</button></div>
    {error&&<div className="banner error">{error}</div>}
    <div className="card table-wrap"><table><thead><tr><th>Employee</th><th>Title</th><th>Category</th><th>Amount</th><th>Date</th><th>Action</th></tr></thead>
    <tbody>{items.map(e=><tr key={e.id}><td>{e.employee_name}<br/><small>{e.department}</small></td><td>{e.title}</td><td>{e.category}</td><td>₹{Number(e.amount).toFixed(2)}</td><td>{e.expense_date}</td><td>
      <button className="success" onClick={()=>approve(e.id)}>Approve</button>
      <input placeholder="Rejection comment" value={comments[e.id]||""} onChange={x=>setComments({...comments,[e.id]:x.target.value})}/>
      <button className="danger" onClick={()=>reject(e.id)}>Reject</button>
    </td></tr>)}</tbody></table>{items.length===0&&<p>No pending approvals.</p>}</div>
  </section>
}
