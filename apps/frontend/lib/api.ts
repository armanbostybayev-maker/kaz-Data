export const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const STATIC_MODE = process.env.NEXT_PUBLIC_STATIC_MODE === "true";
export const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH || "";

export type CatalogIndicator={id:string;slug:string;name_ru:string;name_kk:string;category:string;unit:string;available_levels:string[];periodicity:string;available_periods:string[];source:string;source_url:string;data_path:string;updated_at:string;derived:boolean;diverging:boolean;formula?:string;inputs?:string[]};
export type Catalog={generated_at:string;categories:Array<{id:string;name_ru:string;indicators:CatalogIndicator[]}>};
export type Dataset={indicator:string;unit:string;source_name:string;source_page:string;source_download:string|null;source_updated_at:string;etl_generated_at:string;periodicity:string;territorial_level:string;available_levels:string[];territorial_reference_date:string;geometry_reference_date:string;derived:boolean;formula?:string;inputs?:string[];periods:string[];values:Record<string,Record<string,number>>};

const cache=new Map<string,Promise<any>>();
export async function asset<T>(name:string):Promise<T>{
  if(!cache.has(name)) cache.set(name,fetch(`${BASE_PATH}/data/${name}`,{headers:{Accept:"application/json"}}).then(response=>{
    if(!response.ok) throw new Error(`Static data ${response.status}: ${name}`); return response.json();
  }));
  return cache.get(name) as Promise<T>;
}
export async function catalog():Promise<Catalog>{return asset<Catalog>("catalog.json")}
export async function indicatorMeta(id:string):Promise<CatalogIndicator>{
  const c=await catalog(); const found=c.categories.flatMap(x=>x.indicators).find(x=>x.id===id);
  if(!found) throw new Error(`Unknown indicator: ${id}`); return found;
}
export async function indicatorData(id:string):Promise<Dataset>{const meta=await indicatorMeta(id);return asset<Dataset>(meta.data_path)}

export async function api<T>(path:string):Promise<T>{
  if(STATIC_MODE){
    if(path.startsWith("/api/indicators")) return catalog() as T;
    if(path.startsWith("/api/meta/periods")||path.startsWith("/api/meta/years")){
      const q=new URLSearchParams(path.split("?")[1]||""); return (await indicatorData(q.get("indicator")||"population")).periods.slice().reverse() as T;
    }
    if(path.startsWith("/api/meta/territories")){
      const q=new URLSearchParams(path.split("?")[1]||""); const level=Number(q.get("level")||1);
      const geo=await asset<any>(level===1?"territories-adm1.geojson":"territories-adm2.geojson");
      return geo.features.map((f:any)=>f.properties).sort((a:any,b:any)=>a.name_ru.localeCompare(b.name_ru,"ru")) as T;
    }
    if(path.startsWith("/api/territories/")){
      const kato=path.split("/").at(-1); const collections=await Promise.all([asset<any>("territories-adm1.geojson"),asset<any>("territories-adm2.geojson")]);
      const feature=collections.flatMap(item=>item.features).find(item=>String(item.properties.kato)===kato);
      if(!feature) throw new Error("Territory not found"); return {...feature.properties,geometry:feature.geometry} as T;
    }
    if(path.startsWith("/api/data/timeseries")){
      const q=new URLSearchParams(path.split("?")[1]||""); const data=await indicatorData(q.get("indicator")||"population"); const kato=q.get("kato")||"";
      return data.periods.map(period=>({period,value:data.values[period]?.[kato]??null,unit:data.unit})) as T;
    }
    if(path.startsWith("/api/data/period")){
      const q=new URLSearchParams(path.split("?")[1]||""); const data=await indicatorData(q.get("indicator")||"population");
      return {unit:data.unit,values:data.values[q.get("period")||""]||{}} as T;
    }
  }
  const response=await fetch(`${API}${path}`,{headers:{Accept:"application/json"}}); if(!response.ok) throw new Error(`API ${response.status}`); return response.json();
}

export async function mapData(indicator:string,period:string,level:number):Promise<any>{
  if(!STATIC_MODE) return api(`/api/map/${indicator}?period=${period}&territory_level=${level}`);
  const [geo,data,meta]=await Promise.all([asset<any>(level===1?"territories-adm1.geojson":"territories-adm2.geojson"),indicatorData(indicator),indicatorMeta(indicator)]);
  const levelName=level===1?"region":"district"; const values=meta.available_levels.includes(levelName)?(data.values[period]||{}):{};
  return {...geo,metadata:{...meta,period,available:meta.available_levels.includes(levelName)},features:geo.features.map((feature:any)=>{
    const value=values[String(feature.properties.kato)]; return {...feature,properties:{...feature.properties,value:value??null,unit:data.unit,indicator_name:meta.name_ru,period}};
  })};
}
