export function equalInterval(values, count = 5) {
  const clean = values.filter(Number.isFinite);
  if (!clean.length) return [];
  const min = Math.min(...clean), max = Math.max(...clean);
  if (min === max) return [min, max];
  return Array.from({length: count + 1}, (_, i) => min + ((max - min) * i) / count);
}

export function quantile(values, count = 5) {
  const sorted = values.filter(Number.isFinite).sort((a,b) => a-b);
  if (!sorted.length) return [];
  return Array.from({length: count + 1}, (_, i) => {
    const pos = (sorted.length - 1) * i / count;
    const lo = Math.floor(pos), hi = Math.ceil(pos);
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
  });
}

export function standardDeviation(values) {
  const clean = values.filter(Number.isFinite);
  if (!clean.length) return [];
  const mean = clean.reduce((a,b)=>a+b,0)/clean.length;
  const sd = Math.sqrt(clean.reduce((a,b)=>a+(b-mean)**2,0)/clean.length);
  return [Math.min(...clean), mean-sd, mean, mean+sd, Math.max(...clean)].sort((a,b)=>a-b);
}

export function jenks(values, count = 5) {
  const data = values.filter(Number.isFinite).sort((a,b)=>a-b);
  if (!data.length) return [];
  const k = Math.min(count, data.length), lower = Array.from({length:data.length+1},()=>Array(k+1).fill(0));
  const variance = Array.from({length:data.length+1},()=>Array(k+1).fill(Infinity));
  for(let i=1;i<=k;i++){lower[1][i]=1;variance[1][i]=0;}
  for(let l=2;l<=data.length;l++){
    let sum=0,squares=0,weight=0;
    for(let m=1;m<=l;m++){
      const idx=l-m+1,val=data[idx-1]; weight++; sum+=val; squares+=val*val;
      const v=squares-(sum*sum)/weight, prev=idx-1;
      if(prev) for(let j=2;j<=k;j++) if(variance[l][j]>=v+variance[prev][j-1]){lower[l][j]=idx;variance[l][j]=v+variance[prev][j-1];}
    }
    lower[l][1]=1;variance[l][1]=squares-(sum*sum)/weight;
  }
  const breaks=Array(k+1).fill(0); breaks[0]=data[0];breaks[k]=data.at(-1);
  let end=data.length;
  for(let j=k;j>1;j--){const start=lower[end][j]-1;breaks[j-1]=data[start];end=start;}
  return breaks;
}
