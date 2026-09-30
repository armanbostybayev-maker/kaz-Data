"use client";
import {useQuery} from "@tanstack/react-query";
import {asset,Catalog} from "@/lib/api";
type Coverage={indicator:string;level:string;period:string;expected_territories:number;loaded_territories:number;coverage_pct:number;status:string};
export default function DataStatus(){
 const catalog=useQuery({queryKey:["catalog"],queryFn:()=>asset<Catalog>("catalog.json")});
 const coverage=useQuery({queryKey:["coverage"],queryFn:()=>asset<Coverage[]>("coverage.json")});
 const names=new Map(catalog.data?.categories.flatMap(c=>c.indicators).map(i=>[i.id,i.name_ru]));
 const grouped=Object.values((coverage.data||[]).reduce<Record<string,Coverage[]>>((a,r)=>((a[`${r.indicator}:${r.level}`]??=[]).push(r),a),{}));
 return <main className="statusPage"><a href={`${process.env.NEXT_PUBLIC_BASE_PATH||""}/`}>← Вернуться к карте</a><h1>Статус статистических данных</h1><p>Фактическое покрытие текущей геометрии из результатов ETL. Частичное покрытие ранних лет отражает административные изменения и не заполняется искусственно.</p><table><thead><tr><th>Показатель</th><th>Уровень</th><th>Периоды</th><th>Последний период</th><th>Coverage</th><th>Status</th></tr></thead><tbody>{grouped.map(rows=>{const last=rows.at(-1)!;return <tr key={`${last.indicator}:${last.level}`}><td>{names.get(last.indicator)||last.indicator}</td><td>{last.level}</td><td>{rows[0].period}–{last.period}</td><td>{last.loaded_territories}/{last.expected_territories}</td><td>{last.coverage_pct}%</td><td className={last.status==="ok"?"ok":"partial"}>{last.status==="ok"?"✓":"частично"}</td></tr>})}</tbody></table></main>;
}
