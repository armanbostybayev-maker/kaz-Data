"use client";
import {useEffect,useRef} from "react";
import maplibregl,{Map} from "maplibre-gl";
import {mapData} from "@/lib/api";
import {useAtlas} from "@/lib/store";

export default function MapView(){
 const host=useRef<HTMLDivElement>(null), map=useRef<Map|null>(null);
 const {indicator,year,level,selected,set}=useAtlas();
 useEffect(()=>{if(!host.current||map.current)return;
  const tiles=process.env.NEXT_PUBLIC_OSM_TILES||"https://tile.openstreetmap.org/{z}/{x}/{y}.png";
  map.current=new maplibregl.Map({container:host.current,center:[67.5,48.1],zoom:3.4,minZoom:2,
   style:{version:8,sources:{osm:{type:"raster",tiles:[tiles],tileSize:256,attribution:"© OpenStreetMap contributors"}},layers:[{id:"osm",type:"raster",source:"osm"}]}});
  map.current.addControl(new maplibregl.NavigationControl(),"bottom-right");
  return()=>{map.current?.remove();map.current=null};
 },[]);
 useEffect(()=>{const m=map.current;if(!m)return; const id="territories";
  const load=async()=>{const data=await mapData(indicator,year,level);
   if(m.getLayer("fill"))m.removeLayer("fill"); if(m.getLayer("line"))m.removeLayer("line"); if(m.getSource(id))m.removeSource(id);
   m.addSource(id,{type:"geojson",data});
   m.addLayer({id:"fill",type:"fill",source:id,paint:{"fill-color":["case",["!",["has","value"]],"#d9dedb",["interpolate",["linear"],["to-number",["get","value"]],0,"#d7eee7",500000,"#8ac9b8",1000000,"#2c927f",2000000,"#075b52"]],"fill-opacity":["case",["==",["get","kato"],selected||""],.88,.7]}} as any);
   m.addLayer({id:"line",type:"line",source:id,paint:{"line-color":["case",["==",["get","kato"],selected||""],"#f7c948","#173e3a"],"line-width":["case",["==",["get","kato"],selected||""],3,1]}} as any);
   m.on("click","fill",e=>{const f=e.features?.[0];if(f){set({selected:String(f.properties?.kato)}); const b=new maplibregl.LngLatBounds(); const visit=(c:any)=>typeof c[0]==="number"?b.extend(c):c.forEach(visit);visit((f.geometry as any).coordinates);m.fitBounds(b,{padding:80,maxZoom:8});}});
   m.on("mousemove","fill",e=>{m.getCanvas().style.cursor="pointer"; const f=e.features?.[0]; if(!f)return; const p=f.properties||{}; new maplibregl.Popup({closeButton:false,className:"atlas-tip"}).setLngLat(e.lngLat).setHTML(`<strong>${p.name_ru}</strong><br>${p.value==null?'Нет данных':Number(p.value).toLocaleString('ru-RU')+' '+p.unit}`).addTo(m);});
   m.on("mouseleave","fill",()=>{m.getCanvas().style.cursor="";document.querySelectorAll('.atlas-tip').forEach(n=>n.remove())});
  }; if(m.isStyleLoaded())load().catch(()=>{});else m.once("load",()=>load().catch(()=>{}));
 },[indicator,year,level,selected,set]);
 return <div ref={host} className="map" aria-label="Карта Казахстана"/>;
}
