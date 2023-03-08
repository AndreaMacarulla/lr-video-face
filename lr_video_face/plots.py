# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/06_plots.ipynb.

# %% auto 0
__all__ = ['plot_lr_distributions', 'plot_ROC_curve', 'plot_tippett', 'plot_cllr', 'plot_ece', 'plot_cllr_per_qualitydrop',
           'plot_cllr_per_common_attributes', 'plot_new', 'cllr_new', 'subplot_new']

# %% ../nbs/06_plots.ipynb 3
from typing import Dict, List, Optional
from sklearn.metrics import roc_curve
from lir import Xy_to_Xn, metrics
from lir.ece import plot 

import os
import numpy as np 
import pandas as pd

from matplotlib import pyplot as plt 
import seaborn as sns


# %% ../nbs/06_plots.ipynb 5
def plot_lr_distributions(results:Dict, experiment_directory, save_plots:bool = True, show: Optional[bool] = False):
    """
    Plots the 10log LRs generated for the two hypotheses by the fitted system.
    """
    predicted_log_lrs = np.log10(results["lrs_predicted"])
    plt.figure(figsize=(10, 10), dpi=100)
    points0, points1 = Xy_to_Xn(predicted_log_lrs, np.array(results['y_test']))
    plt.hist(points0, bins=20, alpha=.25, density=True)
    plt.hist(points1, bins=20, alpha=.25, density=True)
    plt.xticks(fontsize = 22)
    plt.yticks(fontsize = 22)
    plt.xlabel(r'$log_{10}$ LR',size = 24)
    plt.ylabel('Density',size = 24)
    
    if save_plots:
        savefig = os.path.join(experiment_directory, "lr_distributions3")
        plt.savefig(savefig, dpi=600)
        plt.close()
    if show:
        plt.show()

# %% ../nbs/06_plots.ipynb 6
def plot_ROC_curve(results:Dict, experiment_directory, save_plots:bool = True, show: Optional[bool] = False):

    norm_distances = np.asarray(results["test_norm_distances"])
    fpr, tpr, thresholds = roc_curve(results['y_test'], 1 - norm_distances)
    plt.figure(figsize=(10, 10), dpi=100)
    plt.plot(fpr, fpr, linestyle='--', label='No Skill')
    plt.plot(fpr, tpr, color='r', label=r'ROC curve')
    plt.xlabel('False positive rate (1 - specificity)')
    plt.ylabel('True positive rate (sensitivity)')
    plt.title('ROC curve')
    plt.legend()
    if save_plots:
        savefig = os.path.join(experiment_directory, "ROC_curve")
        plt.savefig(savefig, dpi=600)
        plt.close()
    if show:
        plt.show()

# %% ../nbs/06_plots.ipynb 7
def plot_tippett(results:Dict, experiment_directory, save_plots:bool = True, show: Optional[bool] = False):
        
    """
    Plots the 10log LRs in a Tippett plot.
    """

    predicted_log_lrs = np.log10(results["lrs_predicted"])

    xplot = np.linspace(
        start=np.min(predicted_log_lrs),
        stop=np.max(predicted_log_lrs),
        num=100
    )

    lr_0, lr_1 = Xy_to_Xn(predicted_log_lrs, np.array(results["y_test"]))

    perc0 = (sum(i > xplot for i in lr_0) / len(lr_0)) * 100
    perc1 = (sum(i > xplot for i in lr_1) / len(lr_1)) * 100

    plt.figure(figsize=(10, 10), dpi=600)
    plt.plot(xplot, perc1, color='b', label=r'LRs given $\mathregular{H_1}$')
    plt.plot(xplot, perc0, color='r', label=r'LRs given $\mathregular{H_2}$')
    plt.axvline(x=0, color='k', linestyle='--')
    plt.xlabel('Log likelihood ratio')
    plt.ylabel('Cumulative proportion')
    plt.title('Tippett plot')
    plt.legend()

    if save_plots:
        savefig = os.path.join(experiment_directory, "tippet_plot")
        plt.savefig(savefig, dpi=600)
        plt.close()
    if show:
        plt.show()

# %% ../nbs/06_plots.ipynb 8
def plot_cllr(results:Dict, experiment_directory, enfsi_years: List[int], cllr_expert_per_year:Dict, 
    cllr_auto_per_year:Dict, embeddingModel, save_plots:bool = True, show: Optional[bool] = False):
    
    """
    Plots cllr value for ENFSI tests. It computes both cllr of automated systems with the cllrs from experts.
    If there is no ENFSI data, this graph does not show.

    # todo: save table with cllr results.
    """

    cllr_auto_df = pd.DataFrame(columns=['Year', 'Expert', 'Cllr'])
    cllr_exp_df = pd.DataFrame(columns=['Year', 'Expert', 'Cllr'])
    years = enfsi_years

    for year in years:
        for cllr_exp in cllr_expert_per_year[year]:
            cllr_exp_df = cllr_exp_df.append({'Year': str(year), 'LR Estimator': "Participant", 'Cllr': cllr_exp},
                                                ignore_index=True)

        cllr_auto = cllr_auto_per_year[year]
        cllr_auto_df = cllr_auto_df.append(
            {'Year': str(year), 'LR Estimator': embeddingModel, 'Cllr': cllr_auto},
            ignore_index=True)


    cllr_df = cllr_exp_df.append(cllr_auto_df)
    #Cada LR estimator va en un color
    paleta = ['orange', 'blue']

    # añadimos el cllr de las imagen promediadas
    if len(results['lrs_predicted_2015']):
        x = metrics.cllr(np.asarray(results['lrs_predicted_2015']), np.asarray(results['y_test_2015']))    
        cllr_df = cllr_df.append({'Year': str(2015), 'LR Estimator': 'Quality weighted Images', 'Cllr': x},
            ignore_index=True)
        paleta.append('red')

    sns.set_style("whitegrid")
    sc_plot = sns.catplot(data=cllr_df, x="Year", y="Cllr", hue="LR Estimator",
                            palette=sns.color_palette(paleta))

    # sc_plot.set_title("Cllrs for Automated system and ENFSI participants")
    # sc_plot.set(xticks=[map(str, years)])

    if save_plots:
        savefig = os.path.join(experiment_directory, "cllr_experts")
        plt.savefig(savefig, dpi=600)
        plt.close()
    if show:
        plt.show()

# %% ../nbs/06_plots.ipynb 9
def plot_ece(results:Dict, experiment_directory, save_plots:bool = True) -> object:
        savefig = os.path.join(experiment_directory, "ECE_plot")
        plot(np.asarray(results["lrs_predicted"]), np.asarray(results["y_test"]), path=savefig, kw_figure={'figsize': (10, 10), 'dpi': 600})

# %% ../nbs/06_plots.ipynb 11
def plot_cllr_per_qualitydrop(cllrs_2015:Dict[float,float], cllr_expert_per_year,
experiment_directory,
save_plots:bool = True, 
show: Optional[bool] = False):
    
    df = pd.DataFrame.from_dict(cllrs_2015, orient='index', columns=['Cllr'])    
    df = df.reset_index(drop = False)
    df.rename(columns={'index': 'Quality Drop'}, inplace=True)
    
    df['legend'] = 'Automatic System'
    
    #df.reset_index(inplace = True)
    # cllr es un valor promedio del error cometido en las observaciones. 
    # como cada observador tiene el mismo número de observaciones, 
    # el promedio global es igual al promedio de los valores obtenidos por cada observador.
    cllr_experts = np.mean(cllr_expert_per_year[2015])

    #para dibujar en la gráfica
    x1 = np.min(df['Quality Drop'])
    x2 = np.max(df['Quality Drop'])    

    df = df.append({'Quality Drop': x1, 'Cllr': cllr_experts, 'legend': 'Participants'}, ignore_index = True)
    df = df.append({'Quality Drop': x2, 'Cllr': cllr_experts, 'legend': 'Participants'}, ignore_index = True)

    #hay que ordenar os datos para que no aparezcan leyendas múltiples
    df.sort_values(by= ['legend', 'Quality Drop'], inplace = True)
    
    sns.set_style("whitegrid")
    sc_plot = sns.lineplot(data=df, x='Quality Drop', y="Cllr", hue = 'legend', marker='s')
    sc_plot.set(xscale="log")

    sc_plot.set_title("Cllrs for Automated system and ENFSI year 2015 according to quality drop")
    # sc_plot.set(xticks=[map(str, years)])

    if save_plots:
        savefig = os.path.join(experiment_directory, "cllr_2015_quality_drop")
        plt.savefig(savefig, dpi=600)
        plt.close()
    if show:
        plt.show()


def plot_cllr_per_common_attributes(results:Dict, cllr_expert_per_year,
experiment_directory,
save_plots:bool = True, 
show: Optional[bool] = False):

    df0 = pd.DataFrame({'lr':results['lrs_predicted'],\
        'y': results['y_test'],\
        'common_attributes':results['common_attributes'],\
        'drop':results['quality_drops']})
        
    
    df0 = df0.loc[(df0['drop']==1)]
    df0 = df0.reset_index(drop = True)
    df = pd.DataFrame()

    for n in np.unique(df0['common_attributes']):
        dfn = df0.loc[(df0['common_attributes'] == n)]
        x = metrics.cllr(np.asarray(dfn['lr']), np.asarray(dfn['y']))    
        df = df.append({'legend': 'Automatic System', 'Common Attributes': n, 'Cllr': x}, ignore_index=True)    

    df = df.reset_index(drop = False)
    
    
    #df.reset_index(inplace = True)
    # cllr es un valor promedio del error cometido en las observaciones. 
    # como cada observador tiene el mismo número de observaciones, 
    # el promedio global es igual al promedio de los valores obtenidos por cada observador.
    cllr_experts = np.mean(cllr_expert_per_year[2015])

    #para dibujar en la gráfica
    x1 = np.min(df['Common Attributes'])
    x2 = np.max(df['Common Attributes'])    

    df = df.append({'legend': 'Participants', 'Common Attributes': x1, 'Cllr': cllr_experts}, ignore_index = True)
    df = df.append({'legend': 'Participants', 'Common Attributes': x2, 'Cllr': cllr_experts}, ignore_index = True)

    #hay que ordenar os datos para que no aparezcan leyendas múltiples
    df.sort_values(by= ['legend', 'Common Attributes'], inplace = True)
    
    sns.set_style("whitegrid")
    sc_plot = sns.lineplot(data=df, x='Common Attributes', y="Cllr", hue = 'legend', marker='s')
    #sc_plot.set(xscale="log")

    sc_plot.set_title("Cllrs for Automated system and ENFSI year 2015 according to number of matching attributes")
    # sc_plot.set(xticks=[map(str, years)])

    if save_plots:
        savefig = os.path.join(experiment_directory, "cllr_2015_common_atts")
        plt.savefig(savefig, dpi=600)
        plt.close()
    if show:
        plt.show()

# %% ../nbs/06_plots.ipynb 12
def plot_new(results:Dict, cllr_expert_per_year,
experiment_directory,
save_plots:bool = True, 
show: Optional[bool] = False):    

    # the results are only received for 2015
    lrs_predicted = results["lrs_predicted"]
    y_test = results["y_test"]
    dropouts = results["quality_drops"]
    common_attributes = results['common_attributes']
    
    cllr_participants = np.mean(cllr_expert_per_year[2015])

    # imagen promedio (17 comparisons)
    lr_avg = results["lrs_predicted_2015"]
    y_avg = results["y_test_2015"]    
    
    cllr_avg = metrics.cllr(np.asarray(lr_avg), np.asarray(y_avg)) 

    #get cllr per dropout

    df_plot1 = pd.DataFrame()
    for d in set(dropouts):
        lr_d = [lr for lr,dropout in zip(lrs_predicted,dropouts) if dropout== d ]
        y_d = [y for y,dropout in zip(y_test,dropouts) if dropout== d ]
        cllr_d = metrics.cllr(np.asarray(lr_d), np.asarray(y_d))
        

        #solo cambio en el momento de plotear
        df_plot1 = df_plot1.append({'dropout': 100*(1-d), 'Cllr': cllr_d},ignore_index = True)

    df_plot1.sort_values(by= 'dropout', inplace = True)
    df_plot1.dropna(inplace= True)

    xa,xb = min(df_plot1.dropout),max(df_plot1.dropout)

    # get cllr per common attributes
    # filter results when dropout = 1 
    lrs = [lr for lr,drop in zip(lrs_predicted,dropouts) if drop== 1]
    ys = [y for y,drop in zip(y_test,dropouts) if drop== 1]
    comatt = [ca for ca,drop in zip(common_attributes,dropouts) if drop== 1]


    df_plot2 = pd.DataFrame()
    for c in set(comatt):
        lr_c = [lr for lr,com in zip(lrs,comatt) if com== c ]
        y_c = [y for y,comm in zip(ys,comatt) if comm== c ]
        cllr_c = metrics.cllr(np.asarray(lr_c), np.asarray(y_c))
        df_plot2 = df_plot2.append({'Common Attributes': c, 'Cllr': cllr_c},ignore_index = True)
        
    df_plot2.sort_values(by= 'Common Attributes', inplace = True)
    df_plot2.dropna(inplace= True)

    # and plot with 2 different x scales

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_ylabel('Cllr')
    ax1.set_xlabel('% of discarded pairs', color = color)
    ax1.plot('dropout','Cllr', data = df_plot1, color = color, marker = 'o', label= 'Quality drop')

    # para engañar a la leyenda 1 metemos un punto de la segunda gráfica, para luego que luego no se vea
    


    ax1.tick_params(axis ='x', labelcolor = color)
   
    

    #ax1.set(xscale="log")

# Adding Twin Axes to plot using dataset_2
    ax2 = ax1.twiny()
    color = 'tab:green'
    ax2.set_xlabel('number of common attributes', color = color)

    ax2.plot('Common Attributes','Cllr', data = df_plot2, color = color, marker= '^', label = "Matching attributes")
    # añadimos un plot nulo solo para que aparezca en la leyenda 1
    ax1.plot(np.nan,np.nan, color = color, marker = '^',label = "Matching attributes")
    
    ax2.tick_params(axis ='x', labelcolor = color)

        #añadimos los dos valores como rectas horizontales (ejes 1)
    ax1.plot( [xa,xb],[cllr_avg,cllr_avg], label = 'Average quality Image', color = 'magenta')
    ax1.plot( [xa,xb],[cllr_participants,cllr_participants], label = 'Participants', linestyle= '--', color = 'black')


    #añadimos la leyenda 1 solo
    #ax1.legend(loc = 'lower center')
    ax1.legend(bbox_to_anchor=(.5, .2))

    
    plt.title("Cllrs per quality drop and number of common attributes")
    # sc_plot.set(xticks=[map(str, years)])

    if save_plots:
        savefig = os.path.join(experiment_directory, "cllr_2015")
        plt.savefig(savefig, dpi=600)
        #plt.show()
        plt.close()
    if show:
        plt.show()

    



# %% ../nbs/06_plots.ipynb 14
def cllr_new(lrs, y, weights=(1, 1)):
    """
    Calculates a log likelihood ratio cost (C_llr) for a series of likelihood
    ratios.

    Nico Brümmer and Johan du Preez, Application-independent evaluation of speaker detection, In: Computer Speech and
    Language 20(2-3), 2006.

    Parameters
    ----------
    lrs : a numpy array of LRs
    y : a numpy array of labels (0 or 1)

    Returns
    -------
    cllr
        the log likelihood ratio cost
    """

    # ignore errors:
    #   divide -> ignore divide by zero
    #   over -> ignore scalar overflow
    
    #normalizamos pesos
    #weights = weights/sum(weights)

    with np.errstate(divide='ignore', over='ignore'):
        lrs0, lrs1 = Xy_to_Xn(lrs, y) 
        cllr0_l =  np.log2(1 + lrs0) if weights[0] > 0 else np.empty()
        cllr1_l =  np.log2(1 + 1 / lrs1) if weights[1] > 0 else np.empty()

        cllr0 = weights[0] * np.mean(cllr0_l) if weights[0] > 0 else 0
        cllr1 = weights[1] * np.mean(cllr1_l) if weights[1] > 0 else 0

        #devolvemos cllr y la lista de valores que lo forman
        return ((cllr0+cllr1)/sum(weights),np.concatenate((cllr0_l,cllr1_l)))

        #cllr0 = weights[0] * np.mean(np.log2(1 + lrs0)) if weights[0] > 0 else 0
        #cllr1 = weights[1] * np.mean(np.log2(1 + 1 / lrs1)) if weights[1] > 0 else 0
        #return (cllr0 + cllr1) / sum(weights)


# %% ../nbs/06_plots.ipynb 16
import csv
import datetime

def subplot_new(ax1,results:Dict, cllr_expert):    

    # the results are only received for 2015
    lrs_predicted = results["lrs_predicted"]
    y_test = results["y_test"]
    dropouts = results["quality_drops"]
    common_attributes = results['common_attributes']
    
    cllr_participants = np.mean(cllr_expert)

    # imagen promedio (17 comparisons)
    lr_avg = results["lrs_predicted_2015"]
    y_avg = results["y_test_2015"]    
    
    cllr_avg = metrics.cllr(np.asarray(lr_avg), np.asarray(y_avg)) 

    #get cllr per dropout
    with open('eggs.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter= '\t')
    


    df_plot1 = pd.DataFrame()
    for d in set(dropouts):
        lr_d = [lr for lr,dropout in zip(lrs_predicted,dropouts) if dropout== d ]
        y_d = [y for y,dropout in zip(y_test,dropouts) if dropout== d ]
        cllr_d = metrics.cllr(np.asarray(lr_d), np.asarray(y_d))

        cllr_d1,cllr_d2 = cllr_new(np.asarray(lr_d), np.asarray(y_d))

        spamwriter.writerow(cllr_d1,np.percentile(cllr_d2,[25,50,75]))
        print(cllr_d1,np.percentile(cllr_d2,[25,50,75]))

        #solo cambio en el momento de plotear
        df_plot1 = df_plot1.append({'dropout': round(100*(1-d)), 'Cllr': cllr_d1,'Cllr2': cllr_d2},ignore_index = True)
        


    df_plot1.sort_values(by= 'dropout', inplace = True)
    df_plot1.dropna(inplace= True)

    #df_plot1.to_excel("cllr_boxplot.xlsx")

    xa,xb = min(df_plot1.dropout),max(df_plot1.dropout)

    # get cllr per common attributes
    # filter results when dropout = 1 
    lrs = [lr for lr,drop in zip(lrs_predicted,dropouts) if drop== 1]
    ys = [y for y,drop in zip(y_test,dropouts) if drop== 1]
    comatt = [ca for ca,drop in zip(common_attributes,dropouts) if drop== 1]


    df_plot2 = pd.DataFrame()
    for c in set(comatt):
        lr_c = [lr for lr,com in zip(lrs,comatt) if com== c ]
        y_c = [y for y,comm in zip(ys,comatt) if comm== c ]
        cllr_c = metrics.cllr(np.asarray(lr_c), np.asarray(y_c))
        df_plot2 = df_plot2.append({'Common Attributes': c, 'Cllr': cllr_c},ignore_index = True)
        
    df_plot2.sort_values(by= 'Common Attributes', inplace = True)
    df_plot2.dropna(inplace= True)

    # and plot with 2 different x scales

    #fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_ylabel('Cllr')
    ax1.set_xlabel('% of discarded pairs', color = color)
    
    ax1.boxplot(df_plot1['Cllr2'],positions=df_plot1['dropout'],sym='',notch = True, manage_ticks = True, whis= 0, widths=1.2, labels=df_plot1['dropout'])
    ax1.plot('dropout','Cllr', data = df_plot1, color = color, marker = 'o', label= 'Quality based drop')

    
    df_0drop = df_plot1.loc[(df_plot1['dropout'] == 0)]
    ax1.scatter('dropout','Cllr', data = df_0drop, color = 'blue', marker = 's', s=[80],  label= 'Pairing all frames')


    # para engañar a la leyenda 1 metemos un punto de la segunda gráfica, para luego que luego no se vea
    


    ax1.tick_params(axis ='x', labelcolor = color,size = 16)
   
    

    #ax1.set(xscale="log")

# Adding Twin Axes to plot using dataset_2
    ax2 = ax1.twiny()
    color = 'tab:green'
    ax2.set_xlabel('number of common attributes', color = color,fontsize = 14)
    ax2.set_xticks(range(0,7),  fontsize = 16)

    ax2.plot('Common Attributes','Cllr', data = df_plot2, color = color, marker= '^', label = "Matching attributes")
    # añadimos un plot nulo solo para que aparezca en la leyenda 1
    ax1.plot(np.nan,np.nan, color = color, marker = '^',label = "Matching attributes")

 
    
    #ax2.tick_params(axis ='x', labelcolor = color)

        #añadimos los dos valores como rectas horizontales (ejes 1)
    ax1.plot( [xa,xb],[cllr_avg,cllr_avg], label = 'Weighted quality image', color = 'magenta')
    ax1.plot( [xa,xb],[cllr_participants,cllr_participants], label = 'Participants', linestyle= '--', color = 'black')
    ax1.plot( [xa,xb],[1,1], label = 'Random system', linestyle= ':', color = 'blue')

    #plots nulos para que aparezcan en la leyenda 2 y la global.
    ax2.plot(np.nan,np.nan,  label= 'Quality based drop', color = 'red', marker = 'o')
    ax2.scatter(np.nan,np.nan, color = 'blue', marker = 's',  label= 'Pairing all frames')
    ax2.plot(np.nan,np.nan, label = 'Weighted quality image', color = 'magenta')
    ax2.plot(np.nan,np.nan, label = 'Participants', linestyle= '--', color = 'black')
    ax2.plot(np.nan,np.nan, label = 'Random system', linestyle= ':', color = 'blue')
    

    #añadimos la leyenda 1 solo
    #ax1.legend(loc = 'lower center')
    #ax1.legend(bbox_to_anchor=(.5, .2))

    # plt.title("Cllrs per quality drop and number of common attributes")
    # sc_plot.set(xticks=[map(str, years)])

    


