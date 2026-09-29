import pandas as pd


def validate_values(data: pd.DataFrame) -> pd.DataFrame:
    issues=[]
    dup=data.duplicated(["kato","indicator","period"],keep=False)
    for r in data[dup].itertuples(): issues.append({"source":r.source_url,"territory":r.kato,"indicator":r.indicator,"period":r.period,"issue_type":"duplicate","message":"Duplicate territory/indicator/period","severity":"error"})
    for r in data[data.value.notna() & data.value.lt(0)].itertuples(): issues.append({"source":r.source_url,"territory":r.kato,"indicator":r.indicator,"period":r.period,"issue_type":"negative_impossible","message":"Negative value for a non-negative indicator","severity":"error"})
    return pd.DataFrame(issues,columns=["source","territory","indicator","period","issue_type","message","severity"])

