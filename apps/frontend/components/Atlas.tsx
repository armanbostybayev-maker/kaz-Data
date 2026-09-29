"use client";
import dynamic from "next/dynamic";
import {useQuery} from "@tanstack/react-query";
import {api} from "@/lib/api";
import {useAtlas} from "@/lib/store";
const MapView=dynamic(()=>import("./MapView"),{ssr:false});
type Indicator={slug:string;name_ru:string;category:string;unit:string;source_url:string;normalization_allowed:string[]};
type Territory={kato:string;name_ru:string;name_kk:string;admin_level:number};
type Point={period:string;year:number;value:number|null;unit:string};

export default function Atlas(){
 const s=useAtlas(); const indicators=useQuery({queryKey:["indicators"],queryFn:()=>api<Indicator[]>("/api/indicators")});
 const years=useQuery({queryKey:["years",s.indicator],queryFn:()=>api<number[]>(`/api/meta/years?indicator=${s.indicator}`)});
 const detail=useQuery({queryKey:["territory",s.selected],queryFn:()=>api<Territory>(`/api/territories/${s.selected}`),enabled:!!s.selected});
 const series=useQuery({queryKey:["series",s.selected,s.indicator],queryFn:()=>api<Point[]>(`/api/data/timeseries?kato=${s.selected}&indicator=${s.indicator}`),enabled:!!s.selected});
 const current=series.data?.find(x=>x.year===s.year); const meta=indicators.data?.find(x=>x.slug===s.indicator);
 const exportCsv=()=>{const rows=series.data||[];const csv=['period,value,unit',...rows.map(r=>`${r.period},${r.value??''},${r.unit}`)].join('\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));a.download=`${s.indicator}-${s.selected||'selection'}.csv`;a.click()};
 return <main className="shell">
  <header><div className="brand"><span className="mark">QZ</span><div><b>Qazaqstan Atlas</b><small>Официальная статистика в пространстве</small></div></div><label className="search">⌕ <input placeholder="Найти область, район или КАТО"/></label><div className="headerActions"><button className="lang">РУ <span>ҚАЗ</span></button><a className="source" href={meta?.source_url||"https://stat.gov.kz/"} target="_blank">Источник данных ↗</a></div></header>
  <aside className="filters"><div className="eyebrow">Параметры карты</div><h1>Статистический<br/>атлас Казахстана</h1>
   <section><h3>Территория</h3><label>Уровень<select value={s.level} onChange={e=>s.set({level:+e.target.value,selected:null})}><option value="1">Области и города</option><option value="2">Районы и города</option></select></label></section>
   <section><h3>Статистика</h3><label>Показатель<select value={s.indicator} onChange={e=>s.set({indicator:e.target.value})}>{indicators.data?.map(i=><option key={i.slug} value={i.slug}>{i.name_ru}</option>)}</select></label><label>Период<select value={s.year} onChange={e=>s.set({year:+e.target.value})}>{(years.data||[2024]).map(y=><option key={y}>{y}</option>)}</select></label><label>Нормализация<select><option>Абсолютное значение</option><option>На душу населения</option><option>Изменение, %</option></select></label></section>
   <section><h3>Визуализация</h3><div className="grid"><label>Классификация<select><option>Jenks</option><option>Квантили</option><option>Равные интервалы</option></select></label><label>Классов<select><option>5</option><option>7</option></select></label></div><label>Подложка<select><option>OSM</option><option disabled>COSMO · настройте URL</option><option disabled>TOPO · настройте URL</option></select></label></section>
   <div className="legend"><div className="legendTitle"><span>Легенда</span><small>{meta?.unit||"—"}</small></div><div className="ramp"/><div className="ticks"><span>меньше</span><span>больше</span></div><div className="nodata"><i/> Нет данных</div></div>
  </aside>
  <section className="mapWrap"><MapView/><div className="mapBadge"><span className="live"/> БНС РК · актуальные публикации</div><div className="zoomHint">Нажмите на регион для детализации</div></section>
  <aside className="details"><div className="eyebrow">Выбранная территория</div>{s.selected?<><div className="crumb">Казахстан / {detail.data?.name_ru}</div><h2>{detail.data?.name_ru||"Загрузка…"}</h2><div className="kato">КАТО {detail.data?.kato}</div><div className="metric"><span>{meta?.name_ru||"Показатель"}</span><strong>{current?.value==null?"Нет данных":Number(current.value).toLocaleString("ru-RU")}</strong><small>{current?.unit||meta?.unit}</small></div><div className="tabs"><button className="active">Динамика</button><button>Сравнение</button><button>Структура</button></div><div className="spark">{(series.data||[]).slice(-12).map((p,i,a)=><i key={p.period} style={{height:`${p.value==null?4:18+60*(p.value/Math.max(...a.map(x=>x.value||0),1))}%`}} title={`${p.period}: ${p.value??'нет данных'}`}/>)}</div><div className="seriesYears"><span>{series.data?.at(-12)?.year||"—"}</span><span>{series.data?.at(-1)?.year||"—"}</span></div><button className="export" onClick={exportCsv}>↓ Экспорт CSV</button></>:<div className="empty"><div className="pin">⌖</div><h2>Выберите территорию</h2><p>Нажмите на область на карте, чтобы увидеть официальные значения и динамику.</p></div>}
   <footer><b>Метаданные</b><span>Источник: Бюро национальной статистики РК</span><span>Пропуски отображаются как «Нет данных»</span></footer>
  </aside>
  <div className="timeline"><button>▶</button><span>{years.data?.at(-1)||2010}</span><input type="range" min="0" max={Math.max((years.data?.length||1)-1,0)} value={Math.max((years.data||[]).indexOf(s.year),0)} onChange={e=>s.set({year:(years.data||[2024])[+e.target.value]})}/><b>{s.year}</b></div>
 </main>
}

