export const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const STATIC_MODE = process.env.NEXT_PUBLIC_STATIC_MODE === "true";
export const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH || "";

async function asset<T>(name:string):Promise<T>{
  const response=await fetch(`${BASE_PATH}/data/${name}`,{headers:{Accept:"application/json"}});
  if(!response.ok) throw new Error(`Static data ${response.status}`);
  return response.json();
}

export async function api<T>(path:string):Promise<T>{
  if(STATIC_MODE){
    if(path.startsWith("/api/indicators")) return asset<T>("indicators.json");
    if(path.startsWith("/api/meta/years")){
      const rows=await asset<Array<{year:number}>>("population.json");
      return [...new Set(rows.map(row=>row.year))].sort((a,b)=>b-a) as T;
    }
    if(path.startsWith("/api/territories/")){
      const kato=path.split("/").at(-1);
      const collections=await Promise.all([asset<any>("territories-adm1.geojson"),asset<any>("territories-adm2.geojson")]);
      const feature=collections.flatMap(item=>item.features).find(item=>String(item.properties.kato)===kato);
      if(!feature) throw new Error("Territory not found");
      return {...feature.properties,geometry:feature.geometry} as T;
    }
    if(path.startsWith("/api/data/timeseries")){
      const query=new URLSearchParams(path.split("?")[1]||"");
      const rows=await asset<Array<Record<string,any>>>("population.json");
      return rows.filter(row=>String(row.kato)===query.get("kato")) as T;
    }
  }
  const response=await fetch(`${API}${path}`,{headers:{Accept:"application/json"}});
  if(!response.ok) throw new Error(`API ${response.status}`);
  return response.json();
}

export async function mapData(indicator:string,year:number,level:number):Promise<any>{
  if(!STATIC_MODE) return api(`/api/map/${indicator}?year=${year}&territory_level=${level}`);
  const [geo,rows]=await Promise.all([
    asset<any>(level===1?"territories-adm1.geojson":"territories-adm2.geojson"),
    asset<Array<Record<string,any>>>("population.json"),
  ]);
  const values=new Map(rows.filter(row=>row.indicator===indicator&&row.year===year).map(row=>[String(row.kato),row]));
  return {...geo,features:geo.features.map((feature:any)=>{
    const row=values.get(String(feature.properties.kato));
    return {...feature,properties:{...feature.properties,value:row?.value??null,unit:row?.unit??"человек"}};
  })};
}
