import React, { useEffect, useState } from "react";
import { apiFetch } from "../api";

const emptyForm = {
  title: "",
  category: "Travel",
  amount: "",
  expense_date: new Date().toISOString().slice(0, 10),
  receipt_filename: "",
  description: "",
};

const categories = ["Travel", "Meals", "Accommodation", "Office Supplies", "Client Entertainment", "Other"];

export default function EmployeePage() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    try {
      setItems(await apiFetch("/expenses"));
      setError("");
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => { load(); }, []);

  function updateField(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function resetForm() {
    setForm(emptyForm);
    setEditingId(null);
  }

  async function save(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    try {
      const payload = { ...form, amount: Number(form.amount) };
      if (editingId) {
        await apiFetch(`/expenses/${editingId}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        });
        setMessage("Expense updated successfully.");
      } else {
        await apiFetch("/expenses", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        setMessage("Expense saved as draft.");
      }
      resetForm();
      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  function edit(item) {
    setEditingId(item.id);
    setForm({
      title: item.title,
      category: item.category,
      amount: item.amount,
      expense_date: item.expense_date,
      receipt_filename: item.receipt_filename || "",
      description: item.description || "",
    });
    setError("");
    setMessage("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function submitExpense(id) {
    try {
      await apiFetch(`/expenses/${id}/submit`, { method: "POST" });
      setMessage("Expense submitted to your manager.");
      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function removeExpense(id) {
    if (!window.confirm("Delete this draft expense?")) return;
    try {
      await apiFetch(`/expenses/${id}`, { method: "DELETE" });
      setMessage("Draft deleted.");
      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <section>
      <div className="page-head">
        <div>
          <h2>My Expenses</h2>
          <p>Create, edit, submit and track your expense reports.</p>
        </div>
        <button onClick={load}>Refresh</button>
      </div>

      {error && <div className="banner error">{error}</div>}
      {message && <div className="banner success-banner">{message}</div>}

      <form className="card expense-form" onSubmit={save}>
        <h3>{editingId ? "Edit Expense" : "New Expense"}</h3>
        <div className="form-grid">
          <div>
            <label>Title</label>
            <input name="title" value={form.title} onChange={updateField} required minLength={2} maxLength={200} />
          </div>
          <div>
            <label>Category</label>
            <select name="category" value={form.category} onChange={updateField}>
              {categories.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label>Amount (₹)</label>
            <input name="amount" type="number" min="0.01" step="0.01" value={form.amount} onChange={updateField} required />
          </div>
          <div>
            <label>Expense Date</label>
            <input name="expense_date" type="date" value={form.expense_date} onChange={updateField} required />
          </div>
          <div>
            <label>Receipt Filename</label>
            <input name="receipt_filename" value={form.receipt_filename} onChange={updateField} placeholder="receipt.pdf" />
          </div>
          <div>
            <label>Description</label>
            <input name="description" value={form.description} onChange={updateField} placeholder="Business purpose" />
          </div>
        </div>
        <div className="form-actions">
          <button className="primary" type="submit">{editingId ? "Update Expense" : "Save Draft"}</button>
          {editingId && <button type="button" onClick={resetForm}>Cancel</button>}
        </div>
      </form>

      <div className="card table-wrap">
        <h3>Expense History</h3>
        <table>
          <thead>
            <tr><th>Title</th><th>Category</th><th>Amount</th><th>Date</th><th>Status</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr key={item.id}>
                <td>{item.title}</td>
                <td>{item.category}</td>
                <td>₹{Number(item.amount).toFixed(2)}</td>
                <td>{item.expense_date}</td>
                <td><span className={`status status-${item.status}`}>{item.status}</span></td>
                <td>
                  {(item.status === "draft" || item.status === "rejected") && <button onClick={() => edit(item)}>Edit</button>}
                  {item.status === "draft" && <button className="primary action-gap" onClick={() => submitExpense(item.id)}>Submit</button>}
                  {item.status === "draft" && <button className="danger" onClick={() => removeExpense(item.id)}>Delete</button>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {items.length === 0 && <p>No expenses found.</p>}
      </div>
    </section>
  );
}
