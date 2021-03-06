import io
import matplotlib.pyplot as plt
from PySide.QtGui import QApplication, QImage

import sys
app = QApplication(sys.argv)

def add_clipboard_to_figures():
    # use monkey-patching to replace the original plt.figure() function with
    # our own, which supports clipboard-copying
    oldfig = plt.figure

    def newfig(*args, **kwargs):
        fig = oldfig(*args, **kwargs)
        def clipboard_handler(event):
            if event.key == 'ctrl+c':
                # store the image in a buffer using savefig(), this has the
                # advantage of applying all the default savefig parameters
                # such as background color; those would be ignored if you simply
                # grab the canvas using Qt
                buf = io.BytesIO()
                fig.savefig(buf)

                blah = QImage.fromData(buf.getvalue())

                QApplication.clipboard().setImage(blah)
                buf.close()

        fig.canvas.mpl_connect('key_press_event', clipboard_handler)
        return fig

    plt.figure = newfig

add_clipboard_to_figures()





import os
import sys
import numpy as np
import scipy as sp
import pandas as pd         # pandas tabular DataFrame for task/behavioral data
import matplotlib as mpl    # plot
import matplotlib.pyplot as plt
import re                   # regular expression
import warnings
import misc_tools


# custom packages
sys.path.append('/shared/homes/sguan/Coding_Projects/PyNeuroSG')
import dg2df  # for reading behavioral data
import PyNeuroAna as pna
import PyNeuroPlot as pnp
import data_load_DLSH


def order_consecutive(x):
    result = [0]
    for i in range(1, len(x)):
        cur = x[i]
        pre = x[i-1]
        if cur==pre:
            result.append(result[-1]+1)
        else:
            result.append(0)
    return np.array(result)


""" get dg files and sort by time """

# dir_dg = '/shared/homes/sguan/neuro_data/stim_dg'
# dir_dg = '/shared/lab/projects/analysis/ryan/data_dg'
dir_dg = 'L:/projects/analysis/ryan/data_dg'
list_name_dg_all = os.listdir(dir_dg)

keyword_dg = 'a.*_080317.*'

_, data_df, name_datafiles = data_load_DLSH.load_data(keyword=keyword_dg, tf_interactive=True, dir_dg=dir_dg, mode='dg')
data_df = data_load_DLSH.standardize_data_df(data_df)
filename_common = misc_tools.str_common(name_datafiles)
data_df['RT'] = data_df['rts'] - data_df['TargetOnset']

resp_rate = 1.0*len(data_df)/data_df['obs_total'][0]

""" use DfPlot """
# pnp.DfPlot(data_df, values='RT', x='TargetOnset', c='side', p='fileindex', plot_type='bar', errbar='se')
pnp.DfPlot(data_df, values='RT', x='TargetOnset', c='side', plot_type='box', title_text='{}, resp_rate={:.2f}'.format(filename_common, resp_rate))




""" train left/right switch """
keyword_dg = 'h.*_071917.*'

_, data_df, name_datafiles = data_load_DLSH.load_data(keyword=keyword_dg, tf_interactive=True, dir_dg=dir_dg, mode='dg')
data_df = data_load_DLSH.standardize_data_df(data_df)
filename_common = misc_tools.str_common(name_datafiles)
data_df['RT'] = data_df['rts'] - data_df['TargetOnset']

resp_rate = 1.0*len(data_df)/data_df['obs_total'][0]
title_text = '{}, resp_rate={:.2f}'.format(filename_common, resp_rate)
pnp.DfPlot(data_df, values='status', x='file', c='side', plot_type='bar', title_text=title_text)
pnp.DfPlot(data_df, values='RT', x='file', c='side', plot_type='box', title_text='{}, resp_rate={:.2f}'.format(filename_common, resp_rate))
pnp.DfPlot(data_df, values='RT', x='side', c='status', plot_type='violin', title_text='{}, resp_rate={:.2f}'.format(filename_common, resp_rate))


reload(pnp); pnp.DfPlot(data_df, values='status', x='file', c='side', title_text=title_text)
reload(pnp); pnp.DfPlot(data_df, values='RT', x='file', c='side', title_text=title_text)
reload(pnp); pnp.DfPlot(data_df, values='status', x='TargetOnset', c='side', title_text=title_text)
reload(pnp); pnp.DfPlot(data_df, values='RT', x='TargetOnset', c='status', p='side', title_text=title_text)



""" train left/right switch """
keyword_dg = 'h.*_072017.*'

_, data_df, name_datafiles = data_load_DLSH.load_data(keyword=keyword_dg, tf_interactive=True, dir_dg=dir_dg, mode='dg')
data_df = data_load_DLSH.standardize_data_df(data_df)
filename_common = misc_tools.str_common(name_datafiles)
data_df['RT'] = data_df['rts'] - data_df['TargetOnset']

reload(pnp); pnp.DfPlot(data_df, values='status', x='TargetOnset', c='side', title_text=title_text)
reload(pnp); pnp.DfPlot(data_df, values='RT', x='TargetOnset', c='status', p='side', title_text=title_text)


""" train left/right switch """
keyword_dg = 'h.*_072117.*'

_, data_df, name_datafiles = data_load_DLSH.load_data(keyword=keyword_dg, tf_interactive=True, dir_dg=dir_dg, mode='dg')
data_df = data_load_DLSH.standardize_data_df(data_df)
filename_common = misc_tools.str_common(name_datafiles)
data_df['RT'] = data_df['rts'] - data_df['TargetOnset']

reload(pnp); pnp.DfPlot(data_df, values='status', x='TargetOnset', c='side', title_text=title_text)
reload(pnp); pnp.DfPlot(data_df, values='RT', x='TargetOnset', c='status', p='side', title_text=title_text)
reload(pnp); pnp.DfPlot(data_df, values='status', x='file', c='side', title_text=title_text)




keyword_dg = 'h.*_072517.*'

_, data_df, name_datafiles = data_load_DLSH.load_data(keyword=keyword_dg, tf_interactive=True, dir_dg=dir_dg, mode='dg')
data_df = data_load_DLSH.standardize_data_df(data_df)
filename_common = misc_tools.str_common(name_datafiles)
data_df['RT'] = data_df['rts'] - data_df['TargetOnset']

resp_rate = 1.0*len(data_df)/data_df['obs_total'][0]
title_text = '{}, resp_rate={:.2f}'.format(filename_common, resp_rate)


pnp.DfPlot(data_df, values='status', x='file', c='side', title_text=title_text)
plt.gcf().set_size_inches(10,5, forward=True)
plt.savefig('./temp_figs/stasus_{}.png'.format(filename_common))
pnp.DfPlot(data_df, values='RT', x='file', c='side', title_text=title_text)
plt.gcf().set_size_inches(10,5, forward=True)
plt.savefig('./temp_figs/RT_{}.png'.format(filename_common))

pnp.DfPlot(data_df, values='status', x='TargetOnset', c='side', title_text=title_text)
pnp.DfPlot(data_df, values='RT', x='TargetOnset', c='status', p='side', title_text=title_text)




""" 0803 """
keyword_dg = 'a.*_080317.*'

_, data_df, name_datafiles = data_load_DLSH.load_data(keyword=keyword_dg, tf_interactive=False, dir_dg=dir_dg, mode='dg')
data_df = data_load_DLSH.standardize_data_df(data_df)
filename_common = misc_tools.str_common(name_datafiles)
data_df['RT'] = data_df['rts'] - data_df['TargetOnset']
data_df['order_consecutive'] = order_consecutive(data_df['side'])

resp_rate = 1.0*len(data_df)/data_df['obs_total'][0]
title_text = '{}, resp_rate={:.2f}'.format(filename_common, resp_rate)


pnp.DfPlot(data_df, values='status', x='file', c='side', title_text=title_text, plot_type='bar', errbar='binom')
plt.gcf().set_size_inches(10,5, forward=True)
plt.savefig('./temp_figs/stasus_{}.png'.format(filename_common))
pnp.DfPlot(data_df, values='RT', x='file', c='side', title_text=title_text, plot_type='box')
plt.gcf().set_size_inches(10,5, forward=True)
plt.savefig('./temp_figs/RT_{}.png'.format(filename_common))

pnp.DfPlot(data_df, values='status', x='TargetOnset', c='side', title_text=title_text)
pnp.DfPlot(data_df, values='RT', x='TargetOnset', c='resp', p='status', title_text=title_text)


pnp.DfPlot(data_df, values='status', x='order_consecutive', c='side', limit=(data_df['order_consecutive']<6)*(data_df['file']>=10), title_text=title_text)
plt.savefig('./temp_figs/status_consecutive_{}.png'.format(filename_common))
pnp.DfPlot(data_df, values='RT', x='order_consecutive', c='side', limit=(data_df['order_consecutive']<6)*(data_df['file']>=9), title_text=title_text)
plt.savefig('./temp_figs/RT_consecutive_{}.png'.format(filename_common))