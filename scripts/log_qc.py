"""Independent CSV well-log quality report and depth-track visualization."""
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

CURVES = ['GR','RHOB','NPHI','RDEP','DTC','CALI','SP','RMED','RSHA']

def inspect_logs(df, well):
    required = {'WELL','DEPTH_MD'}
    if not required.issubset(df.columns):
        raise ValueError(f'Missing columns: {sorted(required-set(df.columns))}')
    selected = df.loc[df['WELL'].astype(str).eq(str(well))].copy()
    if selected.empty:
        raise ValueError(f'Well not found: {well}')
    selected['DEPTH_MD'] = pd.to_numeric(selected['DEPTH_MD'], errors='coerce')
    selected = selected.dropna(subset=['DEPTH_MD']).sort_values('DEPTH_MD')
    if selected.empty:
        raise ValueError('No valid depths for selected well')
    curves = [c for c in CURVES if c in selected]
    if not curves:
        raise ValueError('No supported log curves found')
    for c in curves:
        selected[c] = pd.to_numeric(selected[c], errors='coerce').replace([-999.25,-9999],float('nan'))
    report = pd.DataFrame({'curve':curves,'valid_samples':[selected[c].count() for c in curves], 'missing_pct':[selected[c].isna().mean()*100 for c in curves], 'minimum':[selected[c].min() for c in curves], 'maximum':[selected[c].max() for c in curves]})
    return selected, report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv',type=Path); p.add_argument('--well',required=True)
    p.add_argument('--out',type=Path,default=Path('outputs/qc'))
    args=p.parse_args()
    df=pd.read_csv(args.csv,sep=None,engine='python')
    selected, report=inspect_logs(df,args.well)
    args.out.mkdir(parents=True,exist_ok=True)
    report.to_csv(args.out/'log_quality.csv',index=False)
    curves=report['curve'].tolist()
    fig, axes=plt.subplots(1,len(curves),figsize=(2.3*len(curves),8),sharey=True,squeeze=False)
    for ax,c in zip(axes[0],curves):
        ax.plot(selected[c],selected['DEPTH_MD'],linewidth=.7)
        ax.set_title(c); ax.grid(alpha=.25)
        if c in ('RDEP','RMED','RSHA') and (selected[c]>0).any(): ax.set_xscale('log')
    axes[0,0].invert_yaxis(); axes[0,0].set_ylabel('Measured depth (m)')
    fig.suptitle(f'Well log quality review — {args.well}'); fig.tight_layout()
    fig.savefig(args.out/'well_tracks.png',dpi=150); plt.close(fig)
    print(report.to_string(index=False)); print('Saved to',args.out)

if __name__=='__main__': main()
