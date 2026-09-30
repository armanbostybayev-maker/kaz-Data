"use client";
import {useEffect,useRef} from "react";
import maplibregl,{Map} from "maplibre-gl";
import {mapData} from "@/lib/api";
import {useAtlas} from "@/lib/store";

export default function MapView(){
 const host=useRef<HTMLDivElement>(null),map=useRef<Map|null>(null),popup=useRef<maplibregl.Popup|null>(null);
 const {indicator,period,level,selected,set}=useAtlas();
 useEffect(()=>{if(!host.current||map.current)return;
  const tiles=process.env.NEXT_PUBLIC_OSM_TILES||"https://tile.openstreetmap.org/{z}/{x}/{y}.png";
  map.current=new maplibregl.Map({container:host.current,center:[67.5,48.1],zoom:3.4,minZoom:2,style:{version:8,sources:{osm:{type:"raster",tiles:[tiles],tileSize:256,attribution:"© OpenStreetMap contributors"}},layers:[{id:"osm",type:"raster",source:"osm"}]}});
  map.current.addControl(new maplibregl.NavigationControl(),"bottom-right"); return()=>{map.current?.remove();map.current=null};
 },[]);
 useEffect(()=>{const m=map.current;if(!m)return;let active=true;
  const load=async()=>{const data=await mapData(indicator,period,level);if(!active)return;
   if(m.getLayer("fill"))m.removeLayer("fill");if(m.getLayer("line"))m.removeLayer("line");if(m.getSource("territories"))m.removeSource("territories");
   const values=data.features.map((f:any)=>f.properties.value).filter((v:any)=>typeof v==="number");const min=Math.min(...values,0),max=Math.max(...values,1),span=Math.max(Math.abs(min),Math.abs(max),1);
   m.addSource("territories",{type:"geojson",data});
   const color=data.metadata.diverging?["case",["==",["get","value"],null],"#d9dedb",["interpolate",["linear"],["to-number",["get","value"]],-span,"#9b2f47",0,"#f3f1e7",span,"#08796c"]]:["case",["==",["get","value"],null],"#d9dedb",["interpolate",["linear"],["to-number",["get","value"]],min,"#d7eee7",min+(max-min)*.33,"#8ac9b8",min+(max-min)*.66,"#2c927f",max,"#075b52"]];
   m.addLayer({id:"fill",type:"fill",source:"territories",paint:{"fill-color":color,"fill-opacity":["case",["==",["get","kato"],selected||""],.9,.72]}} as any);
   m.addLayer({id:"line",type:"line",source:"territories",paint:{"line-color":["case",["==",["get","kato"],selected||""],"#f7c948","#173e3a"],"line-width":["case",["==",["get","kato"],selected||""],3,1]}} as any);
  };
  if(m.isStyleLoaded())load().catch(console.error);else m.once("load",()=>load().catch(console.error));return()=>{active=false};
 },[indicator,period,level,selected]);
 useEffect(()=>{const m=map.current;if(!m)return;
  const click=(e:any)=>{const f=e.features?.[0];if(!f)return;set({selected:String(f.properties?.kato)});const b=new maplibregl.LngLatBounds();const visit=(c:any)=>typeof c[0]==="number"?b.extend(c):c.forEach(visit);visit(f.geometry.coordinates);m.fitBounds(b,{padding:80,maxZoom:8})};
  const move=(e:any)=>{m.getCanvas().style.cursor="pointer";const p=e.features?.[0]?.properties;if(!p)return;popup.current?.remove();popup.current=new maplibregl.Popup({closeButton:false,className:"atlas-tip"}).setLngLat(e.lngLat).setHTML(`<strong>${p.name_ru}</strong><br>${p.indicator_name}<br><b>${p.value==null?'Нет данных':Number(p.value).toLocaleString('ru-RU')+' '+p.unit}</b><br>${p.period}`).addTo(m)};
  const leave=()=>{m.getCanvas().style.cursor="";popup.current?.remove()};
  m.on("click","fill",click);m.on("mousemove","fill",move);m.on("mouseleave","fill",leave);return()=>{m.off("click","fill",click);m.off("mousemove","fill",move);m.off("mouseleave","fill",leave)};
 },[set]);
 return <div ref={host} className="map" aria-label="Карта Казахстана"/>;
}
