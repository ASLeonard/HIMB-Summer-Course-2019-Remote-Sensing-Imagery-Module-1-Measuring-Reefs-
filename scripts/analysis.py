import pandas
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats

##name of file within the data directory without csv extension
def loadData(file_):
    return pandas.read_csv(open('../data/{}.csv'.format(file_),'r'))

def plotResolutionBias(df):
    f,ax = plt.subplots()
    sns.stripplot(x='imagery_resolution_m',y='perimeter_m',hue='reef_no', data=df,ax=ax,size=8)

    for reef in (12,16,19):
        ax.axhline(np.median(df.loc[(df['reef_no']==reef) & (df['method']=='imagery')]['perimeter_m']),lw=3,c='darkgray',ls='--',label='Satellite median' if reef==12 else None)
        ax.axhline(np.median(df.loc[(df['reef_no']==reef) & (df['method']=='field')]['perimeter_m']),lw=3,ls=':',c='magenta',label='Field median' if reef==12 else None)
        sns.regplot(data=df.loc[df['reef_no']==reef],x='imagery_resolution_m',y='perimeter_m',ax=ax,scatter=False,label='Regression' if reef==12 else None)

    plt.legend(title='Reefs')
    plt.title('Estimation bias by resolution',fontsize=20)
    f.savefig('../figs/resolution_bias.png', bbox_inches='tight')
    plt.show(block=False)

def plotObserverBias(df):
    observers=('AC', 'ASL', 'MICG', 'NH', 'SF', 'TJQ')
    full_data=[]
    for reef in (12,16,19):
        for obs in observers:
            mean = np.mean(df.loc[(df['observer']==obs) & (df['reef_no']==reef) & (df['method']=='imagery')]['perimeter_m'])
            vals = np.array(df.loc[(df['observer']==obs) & (df['reef_no']==reef) & (df['method']=='imagery')]['perimeter_m'])
            residues = vals - mean
            for res in residues:
                full_data.append({'reef':reef,'Observer':observers.index(obs), 'Residue':res})

    dq=pandas.DataFrame(full_data)
    
    f, ax = plt.subplots()
    sns.violinplot(x='Observer',y='Residue',hue='reef',data=dq,palette='pastel',inner='stick',ax=ax)
    #ax.set_yticklabels(labels=range(len(observers)))
    ax.axhline(0,lw=2,ls='--',c='k')
    plt.title('Anonomised observer Residues by Reef',fontsize=20)
    
    f.savefig('../figs/observer_bias.png', bbox_inches='tight')
    plt.show(block=False)


def plotCorrelation(df):
    data = df.loc[df['platform']=='PlanetExplorer']
    results=[]
    observers=('AC', 'ASL', 'MICG', 'NH', 'SF', 'TJQ')
    for _, row in data.iterrows():
        if np.isnan(row['perimeter_m']) or np.isnan(row['area_m2']):
            continue
        
        ##divergence from expected circular behaviour 
        results.append({'reef':row['reef_no'],'divergence':(row['perimeter_m']**2/(3.14*4))/row['area_m2'],'perimeter':row['perimeter_m'],'obs':row['observer']})

    df = pandas.DataFrame(results)

    f, ax = plt.subplots()
    markers={12:'o',16:'^',19:'D'}
    for reef, marker in markers.items():
        dataframe = df.loc[df['reef']==reef]
        ax.scatter(dataframe['perimeter'],dataframe['divergence'],c=[observers.index(i) for i in dataframe['obs']],cmap='cividis',s=75,marker=marker,label=reef)
        
    ax.axhline(np.nanmedian(df['divergence']),c='darkgray',ls='--',lw=2)

    ax.set_xlabel('Reef size',fontsize=16)
    ax.set_ylabel(r'Shape deformation ($\frac{P^2}{4 \pi} / A$)',fontsize=16)
    plt.legend(title='Reef')
    plt.title('Shape bias by Reef size',fontsize=20)
    f.savefig('../figs/correlation_bias.png', bbox_inches='tight')
    plt.show(block=False)

def crunchStats(df):
    for reef in (16,19):
        imagery = np.array(df.loc[(df['reef_no']==reef) & (df['method']=='imagery')]['perimeter_m'])
        field = np.array(df.loc[(df['reef_no']==reef) & (df['method']=='field')]['perimeter_m'])

        print('Reef size: {}, p_value = {}'.format(reef,scipy.stats.ttest_ind(imagery,field,equal_var=False, nan_policy='omit')[1]))

        
if __name__ == "__main__":
    dx = loadData('rotation_group_c')
    plotResolutionBias(dx)
    plotObserverBias(dx)
    plotCorrelation(dx)
    crunchStats(dx)
