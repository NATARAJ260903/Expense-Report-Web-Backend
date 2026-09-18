export const API_BASE=import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
export async function apiFetch(path,options={}){
  const token=localStorage.getItem("token");
  const res=await fetch(`${API_BASE}${path}`,{
    ...options,
    headers:{"Content-Type":"application/json",...(token?{Authorization:`Bearer ${token}`}:{}) ,...(options.headers||{})}
  });
  let data;
  try { data = await res.json(); } catch { data = {}; }
  if(!res.ok) throw new Error(data.detail || `API error (${res.status})`);
  return data;
}
export async function login(email,role){
  const data=await apiFetch("/auth/login",{method:"POST",body:JSON.stringify({email,role})});
  localStorage.setItem("token",data.token);
  localStorage.setItem("user",JSON.stringify(data.user));
  return data;
}
