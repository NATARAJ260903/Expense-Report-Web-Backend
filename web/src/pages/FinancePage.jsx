import React,{useEffect,useState} from "react";
import {apiFetch} from "../api";
export default function FinancePage(){
  const [items,setItems]=useState([]),[summary,setSummary]=useState(null),[error,setError]=useState("");
  async function load(){try{const [a,b]=await Promise.all([apiFetch("/finance/expenses"),apiFetch("/finance/summary")]);setItems(a);setSummary(b);setError("")}catch(e){setError(e.message)}}
  useEffect(()=>{load()},[]);
  async function paid(id){try{await apiFetch(`/expenses/${id}/mark-paid`,{method:"POST"});load()}catch(e){setError(e.message)}}
  return <section><div className="page-head"><div><h2>Finance Dashboard</h2><p>Approved expenses ready for payment.</p></div><button onClick={load}>Refresh</button></div>
    {error&&<div className="banner error">{error}</div>}
    {summary&&<div className="summary-grid">
      <div className="metric"><span>Submitted</span><b>₹{Number(summary.totals.total_submitted).toFixed(2)}</b></div>
      <div className="metric"><span>Approved</span><b>₹{Number(summary.totals.total_approved).toFixed(2)}</b></div>
      <div className="metric"><span>Paid</span><b>₹{Number(summary.totals.total_paid).toFixed(2)}</b></div>
    </div>}
    <div className="card table-wrap"><h3>Approved Queue</h3><table><thead><tr><th>Employee</th><th>Title</th><th>Category</th><th>Amount</th><th>Date</th><th>Action</th></tr></thead><tbody>
      {items.map(e=><tr key={e.id}><td>{e.employee_name}</td><td>{e.title}</td><td>{e.category}</td><td>₹{Number(e.amount).toFixed(2)}</td><td>{e.expense_date}</td><td><button className="primary" onClick={()=>paid(e.id)}>Mark Paid</button></td></tr>)}
    </tbody></table>{items.length===0&&<p>No approved expenses waiting for payment.</p>}</div>
    {summary&&<div className="card"><h3>Spend by Category</h3><ul>{summary.by_category.map(x=><li key={x.category}>{x.category}: ₹{Number(x.total).toFixed(2)}</li>)}</ul></div>}
  </section>
}
