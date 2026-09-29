export const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export async function api<T>(path:string):Promise<T>{
  const response=await fetch(`${API}${path}`,{headers:{Accept:"application/json"}});
  if(!response.ok) throw new Error(`API ${response.status}`);
  return response.json();
}

