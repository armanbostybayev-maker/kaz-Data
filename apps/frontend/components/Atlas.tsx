"use client";
import dynamic from "next/dynamic";
import {useEffect,useState} from "react";
import {useQuery} from "@tanstack/react-query";
import {api,Catalog} from "@/lib/api";
import {useAtlas} from "@/lib/store";
const MapView=dynamic(()=>import("./MapView"),{ssr:false});
type Territory={kato:string;name_ru:string;name_kk:string;admin_level:number};
type Point={period:string;value:number|null;unit:string};
const format=(value:number|null|undefined,unit?:string)=>value==null?"Нет данных":`${Number(value.toFixed(Math.abs(value)<100?2:0)).toLocaleString("ru-RU")} ${unit||""}`;

export default function Atlas(){
 const s=useAtlas(); const [candidate,setCandidate]=useState("");
 const catalog=useQuery({queryKey:["catalog"],queryFn:()=>api<Catalog>("/api/indicators")});
 const indicators=catalog.data?.categories.flatMap(c=>c.indicators)||[]; const meta=indicators.find(x=>x.id===s.indicator);
 const periods=useQuery({queryKey:["periods",s.indicator],queryFn:()=>api<string[]>(`/api/meta/periods?indicator=${s.indicator}`)});
 const territories=useQuery({queryKey:["territories",s.level],queryFn:()=>api<Territory[]>(`/api/meta/territories?level=${s.level}`)});
 const detail=useQuery({queryKey:["territory",s.selected],queryFn:()=>api<Territory>(`/api/territories/${s.selected}`),enabled:!!s.selected});
 const series=useQuery({queryKey:["series",s.selected,s.indicator],queryFn:()=>api<Point[]>(`/api/data/timeseries?kato=${s.selected}&indicator=${s.indicator}`),enabled:!!s.selected&&s.level===1});
 const snapshot=useQuery({queryKey:["snapshot",s.indicator,s.period],queryFn:()=>api<{unit:string;values:Record<string,number>}>(`/api/data/period?indicator=${s.indicator}&period=${s.period}`)});
 useEffect(()=>{if(periods.data?.length&&!periods.data.includes(s.period))s.set({period:periods.data[0]})},[periods.data,s.period,s.set]);
 const current=series.data?.find(x=>x.period===s.period); const available=meta?.available_levels.includes(s.level===1?"region":"district")!==false;
 const exportCsv=()=>{const rows=series.data||[];const csv=['period,value,unit',...rows.map(r=>`${r.period},${r.value??''},${r.unit}`)].join('\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));a.download=`${s.indicator}-${s.selected||'selection'}.csv`;a.click()};
 const addComparison=()=>{if(candidate&&!s.comparisons.includes(candidate)&&s.comparisons.length<5){s.set({comparisons:[...s.comparisons,candidate]});setCandidate("")}};
 const compare=s.comparisons.map(kato=>({kato,name:territories.data?.find(t=>t.kato===kato)?.name_ru||kato,value:snapshot.data?.values[kato]})).filter(x=>x.value!=null);
 const compareMax=Math.max(...compare.map(x=>Math.abs(x.value||0)),1);
 return <main className="shell">
  <header><div className="brand"><span className="mark">QZ</span><div><b>Qazaqstan Atlas</b><small>Официальная статистика в пространстве</small></div></div><label className="search">⌕ <input placeholder="Найти область, район или КАТО"/></label><div className="headerActions"><a className="lang" href={`${process.env.NEXT_PUBLIC_BASE_PATH||""}/data-status`}>Статус данных</a><a className="source" href={meta?.source_url||"https://stat.gov.kz/"} target="_blank">Источник данных ↗</a></div></header>
  <aside className="filters"><div className="eyebrow">Параметры карты</div><h1>Статистический<br/>атлас Казахстана</h1>
   <section><h3>Территория</h3><label>Уровень<select value={s.level} onChange={e=>s.set({level:+e.target.value,selected:null,comparisons:[]})}><option value="1">Области и города</option><option value="2">Районы и города</option></select></label>{!available&&<div className="warning">Данные доступны только на уровне областей</div>}</section>
   <section><h3>Статистика</h3><label>Показатель<select value={s.indicator} onChange={e=>{const next=indicators.find(i=>i.id===e.target.value);s.set({indicator:e.target.value,period:next?.available_periods.at(-1)||"",comparisons:[]})}}>{catalog.data?.categories.map(c=><optgroup key={c.id} label={c.name_ru}>{c.indicators.map(i=><option key={i.id} value={i.id}>{i.name_ru}</option>)}</optgroup>)}</select></label><label>Период<select value={s.period} onChange={e=>s.set({period:e.target.value})}>{(periods.data||[]).map(p=><option key={p}>{p}</option>)}</select></label></section>
   <section><h3>Визуализация</h3><label>Классификация<select disabled><option>{meta?.diverging?"Расходящаяся от нуля":"По диапазону значений"}</option></select></label><label>Подложка<select><option>OSM</option></select></label></section>
   <div className="legend"><div className="legendTitle"><span>{meta?.name_ru||"Легенда"}</span><small>{meta?.unit||"—"}</small></div><div className={`ramp ${meta?.diverging?"diverging":""}`}/><div className="ticks"><span>{meta?.diverging?"отрицательные":"меньше"}</span><span>{meta?.diverging?"положительные":"больше"}</span></div><div className="nodata"><i/> Нет данных</div></div>
  </aside>
  <section className="mapWrap"><MapView/><div className="mapBadge"><span className="live"/> БНС РК · реальные выгрузки</div><div className="zoomHint">Нажмите на регион для детализации</div></section>
  <aside className="details"><div className="eyebrow">Выбранная территория</div>{s.selected?<><div className="crumb">Казахстан / {detail.data?.name_ru}</div><h2>{detail.data?.name_ru||"Загрузка…"}</h2><div className="kato">КАТО {detail.data?.kato}</div><div className="metric"><span>{meta?.name_ru||"Показатель"}</span><strong>{current?.value==null?"Нет данных":Number(current.value.toFixed(Math.abs(current.value)<100?2:0)).toLocaleString("ru-RU")}</strong><small>{current?.value==null?"":current?.unit||meta?.unit}</small><em>{s.period}</em></div><div className="tabs"><button className="active">Динамика</button><button>Сравнение</button></div><div className="spark">{(series.data||[]).slice(-16).map((p,i,a)=><i key={p.period} style={{height:`${p.value==null?4:18+60*(Math.abs(p.value)/Math.max(...a.map(x=>Math.abs(x.value||0)),1))}%`}} title={`${p.period}: ${format(p.value,p.unit)}`}/>)}</div><div className="seriesYears"><span>{series.data?.at(-16)?.period||"—"}</span><span>{series.data?.at(-1)?.period||"—"}</span></div><button className="export" onClick={exportCsv}>↓ Экспорт CSV</button></>:<div className="empty"><div className="pin">⌖</div><h2>Выберите территорию</h2><p>Нажмите на область на карте, чтобы увидеть официальные значения и динамику.</p></div>}
   <div className="compare"><b>Сравнение регионов (2–5)</b><div className="compareAdd"><select value={candidate} onChange={e=>setCandidate(e.target.value)}><option value="">Выберите регион</option>{territories.data?.filter(t=>!s.comparisons.includes(t.kato)).map(t=><option key={t.kato} value={t.kato}>{t.name_ru}</option>)}</select><button onClick={addComparison} disabled={!candidate||s.comparisons.length>=5}>+</button></div>{compare.map(x=><div className="barRow" key={x.kato}><span>{x.name}<button onClick={()=>s.set({comparisons:s.comparisons.filter(k=>k!==x.kato)})}>×</button></span><i style={{width:`${Math.max(3,Math.abs(x.value||0)/compareMax*100)}%`}}/><small>{format(x.value,snapshot.data?.unit)}</small></div>)}</div>
   <footer><b>Метаданные</b><span>Источник: Бюро национальной статистики РК</span><span>Обновлено: {meta?.updated_at||"—"}</span>{meta?.derived&&<span>Расчёт: {meta.formula}</span>}<a href={meta?.source_url} target="_blank">Открыть источник ↗</a><span>NULL отображается как «Нет данных»</span></footer>
  </aside>
  <div className="timeline"><button>▶</button><span>{periods.data?.at(-1)||"—"}</span><input type="range" min="0" max={Math.max((periods.data?.length||1)-1,0)} value={Math.max((periods.data||[]).indexOf(s.period),0)} onChange={e=>s.set({period:(periods.data||[])[+e.target.value]||s.period})}/><b>{s.period}</b></div>
 </main>
}
