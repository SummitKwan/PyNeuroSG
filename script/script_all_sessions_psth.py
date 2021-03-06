
""" script to load all dataset and get the six conditions, designed to run on Pogo """

import os
import sys
import numpy as np
import scipy as sp
import pandas as pd         # pandas tabular DataFrame for task/behavioral data
import matplotlib as mpl    # plot
import matplotlib.pyplot as plt
import re                   # regular expression
import time                 # time code execution
import cPickle as pickle


import dg2df                # for DLSH dynamic group (behavioral data)
import neo                  # data structure for neural data
import quantities as pq
import signal_align         # in this package: align neural data according to task
import PyNeuroAna as pna    # in this package: analysis
import PyNeuroPlot as pnp   # in this package: plot
import misc_tools           # in this package: misc

import data_load_DLSH       # package specific for DLSH lab data

from scipy import signal
from scipy.signal import spectral
from PyNeuroPlot import center2edge


from GM32_layout import layout_GM32


""" load data """
try:
    dir_tdt_tank='/shared/lab/projects/encounter/data/TDT/'
    list_name_tanks = os.listdir(dir_tdt_tank)
except:
    dir_tdt_tank = '/Volumes/Labfiles/projects/encounter/data/TDT/'
    list_name_tanks = os.listdir(dir_tdt_tank)
keyword_tank = '.*GM32.*U16'
list_name_tanks = [name_tank for name_tank in list_name_tanks if re.match(keyword_tank, name_tank) is not None]
list_name_tanks_0 = [name_tank for name_tank in list_name_tanks if re.match('Dante.*', name_tank) is None]
list_name_tanks_1 = [name_tank for name_tank in list_name_tanks if re.match('Dante.*', name_tank) is not None]
list_name_tanks = sorted(list_name_tanks_0) + sorted(list_name_tanks_1)

block_type = 'srv_mask'
# block_type = 'matchnot'
if block_type == 'matchnot':
    t_plot = [-0.200, 1.100]
else:
    t_plot = [-0.100, 0.500]


def GetGroupAve(tankname, signal_type='spk'):
    try:
        [blk, data_df, name_tdt_blocks] = data_load_DLSH.load_data('d_.*{}.*'.format(block_type), tankname, tf_interactive=False,
                                                               dir_tdt_tank='/shared/homes/sguan/neuro_data/tdt_tank',
                                                               dir_dg='/shared/homes/sguan/neuro_data/stim_dg')
    except:
        [blk, data_df, name_tdt_blocks] = data_load_DLSH.load_data('d_.*srv_mask.*', tankname, tf_interactive=False)

    """ Get StimOn time stamps in neo time frame """
    ts_StimOn = data_load_DLSH.get_ts_align(blk, data_df, dg_tos_align='stimon')

    """ some settings for saving figures  """
    filename_common = misc_tools.str_common(name_tdt_blocks)
    dir_temp_fig = './temp_figs'

    """ make sure data field exists """
    data_df = data_load_DLSH.standardize_data_df(data_df, filename_common)
    blk = data_load_DLSH.standardize_blk(blk)

    if signal_type=='spk':
        data_neuro = signal_align.blk_align_to_evt(blk, ts_StimOn, t_plot, type_filter='spiketrains.*',
                                                       name_filter='.*Code[1-9]$', spike_bin_rate=1000,
                                                       chan_filter=range(1, 48 + 1))
    else:
        data_neuro = signal_align.blk_align_to_evt(blk, ts_StimOn, t_plot, type_filter='ana.*',
                                                       name_filter='LFPs.*',
                                                       chan_filter=range(1, 48 + 1))
    data_neuro = signal_align.neuro_sort(data_df, ['stim_familiarized', 'mask_opacity_int'], [], data_neuro)

    ts = data_neuro['ts']
    signal_info = data_neuro['signal_info']
    cdtn = data_neuro['cdtn']
    data_groupave = pna.GroupAve(data_neuro)

    return [data_groupave, ts, signal_info, cdtn]


def GetAllData(tankname, signal_type='spk'):
    try:
        [blk, data_df, name_tdt_blocks] = data_load_DLSH.load_data('d_.*{}.*'.format(block_type), tankname, tf_interactive=False,
                                                               dir_tdt_tank='/shared/homes/sguan/neuro_data/tdt_tank',
                                                               dir_dg='/shared/homes/sguan/neuro_data/stim_dg')
    except:
        [blk, data_df, name_tdt_blocks] = data_load_DLSH.load_data('d_.*srv_mask.*', tankname, tf_interactive=False)

    """ Get StimOn time stamps in neo time frame """
    ts_StimOn = data_load_DLSH.get_ts_align(blk, data_df, dg_tos_align='stimon')

    """ some settings for saving figures  """
    filename_common = misc_tools.str_common(name_tdt_blocks)
    dir_temp_fig = './temp_figs'

    """ make sure data field exists """
    data_df = data_load_DLSH.standardize_data_df(data_df, filename_common)
    blk = data_load_DLSH.standardize_blk(blk)

    if signal_type=='spk':
        data_neuro = signal_align.blk_align_to_evt(blk, ts_StimOn, t_plot, type_filter='spiketrains.*',
                                                       name_filter='.*Code[1-9]$', spike_bin_rate=1000,
                                                       chan_filter=range(1, 48 + 1))
    else:
        data_neuro = signal_align.blk_align_to_evt(blk, ts_StimOn, t_plot, type_filter='ana.*',
                                                       name_filter='LFPs.*',
                                                       chan_filter=range(1, 48 + 1))
    data_neuro = signal_align.neuro_sort(data_df, ['stim_familiarized', 'mask_opacity_int'], [], data_neuro)

    ts = data_neuro['ts']
    signal_info = data_neuro['signal_info']

    return [data_neuro, data_df, ts]


""" store spk or lfp of all sessions """
signal_type='spk'
# signal_type='lfp'

list_data_groupave = []
list_data_neuro = []
list_data_df = []
list_ts = []
list_cdtn = []
list_signal_info = []
list_date = []

if False:  # do not use, because the resulting file is too big (~400G)
    for tankname in list_name_tanks:
        try:
            [data_neuro, data_df, ts] = GetAllData(tankname, signal_type=signal_type)
            list_data_neuro.append(data_neuro)
            list_data_df.append(data_df)
            list_ts.append(ts)
            list_date.append(re.match('.*-(\d{6})-\d{6}', tankname).group(1))
            pickle.dump([list_data_neuro, list_data_df, list_ts, list_date],
                        open('/shared/homes/sguan/Coding_Projects/support_data/DataAll_{}_{}'.format(block_type, signal_type), "wb"))
        except:
            print('tank {} can not be processed'.format(tankname))
    pickle.dump([list_data_neuro, list_data_df, list_ts, list_date],
                        open('/shared/homes/sguan/Coding_Projects/support_data/DataAll_{}_{}'.format(block_type, signal_type), "wb"))


for tankname in list_name_tanks:
    try:
        [data_groupave, ts, signal_info, cdtn] = GetGroupAve(tankname, signal_type=signal_type)
        list_data_groupave.append(data_groupave)
        list_ts.append(ts)
        list_signal_info.append(signal_info)
        list_cdtn.append(cdtn)
        list_date.append(re.match('.*-(\d{6})-\d{6}', tankname).group(1))
        pickle.dump([list_data_groupave, list_ts, list_signal_info, list_cdtn, list_date],
                    open('/shared/homes/sguan/Coding_Projects/support_data/GroupAve_{}_{}'.format(block_type, signal_type), "wb"))
    except:
        pass
pickle.dump([list_data_groupave, list_ts, list_signal_info, list_cdtn, list_date],
                    open('/shared/homes/sguan/Coding_Projects/support_data/GroupAve_{}_{}'.format(block_type, signal_type), "wb"))



"""  V4, TEd and TEm neurons """
block_type = 'srv_mask'
# block_type = 'matchnot'
signal_type='spk'
# signal_type='lfp'
[list_data_groupave, list_ts, list_signal_info, list_cdtn, list_date] = pickle.load(open('/shared/homes/sguan/Coding_Projects/support_data/GroupAve_{}_{}'.format(block_type, signal_type)))


def GetDataCat( list_data_groupave, list_ts, list_signal_info, list_cdtn, list_date ):
    # add date to signal_info
    list_signal_info_date = []
    for signal_info, date in zip(list_signal_info, list_date):
        signal_info_date = pd.DataFrame(signal_info)
        signal_info_date['date'] = date
        list_signal_info_date.append(signal_info_date)
    return [np.dstack(list_data_groupave), list_ts[0], pd.concat(list_signal_info_date, ignore_index=True), list_cdtn[0]]

[data_groupave, ts, signal_info, cdtn] = GetDataCat( list_data_groupave, list_ts, list_signal_info, list_cdtn, list_date )

if signal_type == 'lfp':
    data_groupave = data_groupave*10**6
    sk_std = 0.002
    ylabel = 'uV'
    laminar_range_ave = 1
else:
    sk_std = 0.007
    # ylabel = 'spk/sec'
    ylabel = 'normalized firing rate'
    laminar_range_ave = 1

# the brain area of the recording day
date_area = dict()
date_area['161015'] = 'TEd'
date_area['161023'] = 'TEm'
date_area['161026'] = 'TEm'
date_area['161029'] = 'TEd'
date_area['161118'] = 'TEm'
date_area['161121'] = 'TEm'
date_area['161125'] = 'TEm'
date_area['161202'] = 'TEm'
date_area['161206'] = 'TEd'
date_area['161222'] = 'TEm'
date_area['161228'] = 'TEd'
date_area['170103'] = 'TEd'
date_area['170106'] = 'TEm'
date_area['170113'] = 'TEd'
date_area['170117'] = 'TEd'
date_area['170214'] = 'TEd'
date_area['170221'] = 'TEd'

# the channel index (count from zero) of the granular layer
indx_g_layer = dict()
indx_g_layer['161015'] = 8
indx_g_layer['161023'] = np.nan
indx_g_layer['161026'] = 8
indx_g_layer['161029'] = 9
indx_g_layer['161118'] = 6
indx_g_layer['161121'] = 4
indx_g_layer['161125'] = 5
indx_g_layer['161202'] = 5
indx_g_layer['161206'] = 8
indx_g_layer['161222'] = 6
indx_g_layer['161228'] = 7
indx_g_layer['170103'] = 7
indx_g_layer['170106'] = 2
indx_g_layer['170113'] = 9
indx_g_layer['170117'] = 6
indx_g_layer['170214'] = np.nan
indx_g_layer['170221'] = np.nan

depth_from_g = dict()
for (date, area) in date_area.items():
    if area == 'TEm':
        depth = np.arange(16,0,-1)-1 - indx_g_layer[date]
    elif area == 'TEd':
        depth =   np.arange(16) - indx_g_layer[date]
    depth_from_g[date] = depth


signal_info['area'] = [date_area[i] for i in signal_info['date'].tolist()]
depth_neuron = np.zeros(len(signal_info))*np.nan
for i in range(len(signal_info)):
    if signal_info['channel_index'][i]>32:
        ch = signal_info['channel_index'][i]-33
        depth = depth_from_g[signal_info['date'][i]][ch]
        depth_neuron[i]=depth
signal_info['depth'] = depth_neuron


""" compare three areas """
def cal_psth_std(neuron_keep):
    data_smooth = pna.SmoothTrace(data_groupave[:,:, neuron_keep], ts=ts, sk_std=sk_std, axis=1)
    if signal_type == 'spk':
        data_norm = data_smooth / (np.mean(data_smooth, axis=(0,1)) + 5)   # soft normalize
    else:
        data_norm = (data_smooth- np.mean(data_smooth, axis=(0,1), keepdims=True)) / np.std(data_smooth, axis=(0,1), keepdims=True)
    psth_mean = np.mean(data_norm, axis=2)
    psth_std = np.std(data_norm, axis=2)
    return psth_mean, psth_std, data_norm
def t_test_score(data_norm):
    t_nf_00, p_nf_00 = sp.stats.ttest_1samp(data_norm[0, :, :] - data_norm[3, :, :], 0, axis=1)
    t_nf_50, p_nf_50 = sp.stats.ttest_1samp(data_norm[1, :, :] - data_norm[4, :, :], 0, axis=1)
    t_nf_70, p_nf_70 = sp.stats.ttest_1samp(data_norm[2, :, :] - data_norm[5, :, :], 0, axis=1)
    t_ns_no, p_ns_no = sp.stats.ttest_1samp(data_norm[0, :, :] - data_norm[2, :, :], 0, axis=1)
    t_ns_fa, p_ns_fa = sp.stats.ttest_1samp(data_norm[3, :, :] - data_norm[5, :, :], 0, axis=1)
    return np.vstack([t_nf_00, t_nf_50, t_nf_70, t_ns_no, t_ns_fa])
def d_test_score(data_norm):
    d_nf_00 = pna.cal_CohenD(data_norm[0, :, :], data_norm[3, :, :], axis=1, type_test='paired')
    d_nf_50 = pna.cal_CohenD(data_norm[1, :, :], data_norm[4, :, :], axis=1, type_test='paired')
    d_nf_70 = pna.cal_CohenD(data_norm[2, :, :], data_norm[5, :, :], axis=1, type_test='paired')
    d_ns_no = pna.cal_CohenD(data_norm[0, :, :], data_norm[2, :, :], axis=1, type_test='paired')
    d_ns_fa = pna.cal_CohenD(data_norm[3, :, :], data_norm[5, :, :], axis=1, type_test='paired')
    return np.vstack([d_nf_00, d_nf_50, d_nf_70, d_ns_no, d_ns_fa])

colors = np.vstack([pnp.gen_distinct_colors(3, luminance=0.9), pnp.gen_distinct_colors(3, luminance=0.6)])
linestyles = ['--', '--', '--', '-', '-', '-']
colors_p     = np.vstack([pnp.gen_distinct_colors(3, luminance=0.9), [0.4,0.4,0.4,1], [0,0,0,1]])
linestyles_p = ['-', '-', '-', '--', '--']

plot_highlight = ''
if plot_highlight == 'nov':
    alphas = [1,1,1,0,0,0]
    alphas_p = [0, 0, 0, 1, 0]
elif plot_highlight == 'fam':
    alphas = [0,0,0,1,1,1]
    alphas_p = [0, 0, 0, 0, 1]
elif plot_highlight == '00':
    alphas = [1,0,0,1,0,0]
    alphas_p = [1, 0, 0, 0, 0]
elif plot_highlight == '50':
    alphas = [0,1,0,0,1,0]
    alphas_p = [0, 1, 0, 0, 0]
elif plot_highlight == '70':
    alphas = [0,0,1,0,0,1]
    alphas_p = [0, 0, 1, 0, 0]
elif plot_highlight == '':
    alphas = [1, 1, 1, 1, 1, 1]
    alphas_p = [1, 1, 1, 1, 1]
else:
    alphas = [1, 1, 1, 1, 1, 1]
    alphas_p = [0.5, 0.5, 0.5, 0.5, 0.5]

t_thrhd = 4
def plot_psth_p(neuron_keep):
    N_neuron = np.sum(neuron_keep)
    [psth_mean, psth_std, data_norm] = cal_psth_std(neuron_keep)
    t_values = t_test_score(data_norm)
    d_values = d_test_score(data_norm)

    for i in range(psth_mean.shape[0]):
        plt.plot(ts, psth_mean[i, :], color=colors[i], linestyle=linestyles[i], alpha=alphas[i])
        plt.fill_between(ts, psth_mean[i, :] - psth_std[i, :] / np.sqrt(N_neuron),
                         psth_mean[i, :] + psth_std[i, :] / np.sqrt(N_neuron), color=colors[i], alpha=0.2*alphas[i])
    plt.xlabel('t (s)')
    plt.ylabel(ylabel)

    h_ax_top = pnp.add_sub_axes(h_axes=plt.gca(), size=0.4, loc='top')
    plt.axes(h_ax_top)
    thrhd_d_small = 0.2
    thrhd_d_medium = 0.5
    for i, d in enumerate(d_values):
        plt.fill_between(ts, -i + d, -i, color=colors_p[i], alpha=0.1*alphas_p[i])
        plt.fill_between(ts, -i + d, -i, where=np.abs(d) >= thrhd_d_small, color=colors_p[i], alpha=0.3*alphas_p[i])
        plt.fill_between(ts, -i + d, -i, where=np.abs(d) >= thrhd_d_medium, color=colors_p[i], alpha=0.7*alphas_p[i])
    plt.ylim([-len(d_values),1])
    plt.ylabel('d stat for effect size')
    plt.yticks([])
    # for i, t in enumerate(t_values):
    #     plt.plot(ts[np.abs(t) > t_thrhd], -(i + 1) * 0.1 * np.ones(np.sum( np.abs(t) > t_thrhd)), '|', color=colors_p[i], alpha=alphas_p[i])
    # for i, t in enumerate(t_values):
    #     shift_t_plot = -3 if signal_type =='lfp' else -1
    #     plt.plot(ts[np.abs(t) > t_thrhd], shift_t_plot-(i + 1) * 0.1 * np.ones(np.sum( np.abs(t) > t_thrhd)), '|', color=colors_p[i], alpha=alphas_p[i])

[h_fig, h_ax]=plt.subplots(nrows=1, ncols=3, sharex='all', sharey='all', figsize=[12,5])

plt.axes(h_ax[0])
neuron_keep = ( signal_info['channel_index']<=32)
plot_psth_p(neuron_keep)
plt.title('V4, N={}'.format(np.sum(neuron_keep)))

plt.axes(h_ax[1])
neuron_keep = ( signal_info['channel_index']>32) * (signal_info['area']=='TEd')
plot_psth_p(neuron_keep)
plt.title('TEd, N={}'.format(np.sum(neuron_keep)))

plt.axes(h_ax[2])
neuron_keep = ( signal_info['channel_index']>32) * (signal_info['area']=='TEm')
plot_psth_p(neuron_keep)
plt.title('TEm, N={}'.format(np.sum(neuron_keep)))

plt.axes(h_ax[2])
plt.xticks(np.arange(-0.1,0.5+0.01,0.1))
# plt.legend(cdtn)
h_legend = plt.legend(['nov, 0%', 'nov,50%', 'nov,70%', 'fam, 0%', 'fam,50%', 'fam,70%'], loc='upper left', bbox_to_anchor=(0.9, 1.05))
plt.setp(h_legend.texts, family='monospace')
plt.suptitle('PSTH by area {} {}'.format(block_type, signal_type))
plt.savefig('./temp_figs/PSTH_by_area_{}_{}_{}.pdf'.format(block_type, signal_type, plot_highlight))
plt.savefig('./temp_figs/PSTH_by_area_{}_{}_{}.png'.format(block_type, signal_type, plot_highlight))




""" compare laminar difference for IT TEd and TEm """
colors = np.vstack([pnp.gen_distinct_colors(3, luminance=0.9), pnp.gen_distinct_colors(3, luminance=0.7)])
linestyles = ['--', '--', '--', '-', '-', '-']


# plot in one panel
range_l = range(-8,9,2)
def plot_psth_by_depth(area='TEd'):
    scale_depth=1.0 if signal_type=='spk' else 3.0
    [h_fig, h_ax]=plt.subplots(nrows=1, ncols=6, sharex='all', sharey='all', figsize=[10,8])
    for l in range_l:
        neuron_keep = (signal_info['channel_index'] > 32) * (signal_info['area']==area) * (np.abs(signal_info['depth']-l)<=laminar_range_ave)
        if np.sum(neuron_keep)>0:
            psth, _, _ = cal_psth_std(neuron_keep)
            for j in range(6):
                plt.axes(h_ax[j])
                if j==0:
                    plt.text(ts[0], l+0.2, '{}N'.format(np.sum(neuron_keep)))
                    plt.title('all')
                    alphas = [1, 1, 1, 1, 1, 1]
                elif j==1:
                    plt.title('nov')
                    alphas = [1, 1, 1, 0, 0, 0]
                elif j == 2:
                    plt.title('fam')
                    alphas = [0, 0, 0, 1, 1, 1]
                elif j==3:
                    plt.title('noise 0%')
                    alphas = [1, 0, 0, 1, 0, 0]
                elif j==4:
                    plt.title('noise 50%')
                    alphas = [0, 1, 0, 0, 1, 0]
                elif j==5:
                    plt.title('noise 70%')
                    alphas = [0, 0, 1, 0, 0, 1]
                for i in range(psth.shape[0]):
                    plt.plot(ts, psth[i, :]/scale_depth+l, color=colors[i], linestyle=linestyles[i], alpha=alphas[i])
                # plt.ylabel(ylabel)
    plt.xlim([ts[0], ts[-1]])
    plt.xticks([-0.1,0,0.1,0.2,0.3,0.4,0.5], ['','0','','0.2','','0.4',''])
    plt.yticks(range_l)
    h_fig.text(0.5, 0.04, 'time from stim onset (s)', ha='center')
    h_fig.text(0.04, 0.5, 'laminar position (0.1 mm), [+ for SG, - for IG]', va='center', rotation='vertical')
    plt.suptitle('{} by depth'.format(area))
    plt.savefig('./temp_figs/PSTH_{}_by_depth_{}_{}.pdf'.format(area, block_type, signal_type))
    plt.savefig('./temp_figs/PSTH_{}_by_depth_{}_{}.png'.format(area, block_type, signal_type))

plot_psth_by_depth(area='TEd')
plot_psth_by_depth(area='TEm')



""" V4 by RF location: fovea vs peripheral """


list_chan_fov = [1,2,3,4,6,7,8,11,12,17,18]
list_chan_per = [5,9,10,15,16,20,21,22,25,26,28,32]

[h_fig, h_ax]=plt.subplots(nrows=1, ncols=2, sharex=True, sharey=True, figsize=[12,5])
p_thrhd = 0.05

plt.axes(h_ax[0])
neuron_keep = ( np.in1d(signal_info['channel_index'], list_chan_fov))
plot_psth_p(neuron_keep)
plt.title('V4 fovea, N={}'.format(np.sum(neuron_keep)))

plt.axes(h_ax[1])
neuron_keep = ( np.in1d(signal_info['channel_index'], list_chan_per))
plot_psth_p(neuron_keep)
plt.title('V4 periphral, N={}'.format(np.sum(neuron_keep)))

plt.suptitle('V4 by RF')
plt.savefig('./temp_figs/PSTH_V4_by_RF_{}_{}.pdf'.format(block_type, signal_type))
plt.savefig('./temp_figs/PSTH_V4_by_RF_{}_{}.png'.format(block_type, signal_type))



[h_fig, h_ax]=pnp.create_array_layout_subplots(layout_GM32, tf_linear_indx=True)
h_fig.set_size_inches([10, 9], forward=True)
plt.tight_layout(pad=0.05)
for ch in range(1,32+1):
    plt.axes(h_ax[ch-1])
    neuron_keep = ( signal_info['channel_index']==ch)
    try:
        plot_psth_p(neuron_keep)
    except:
        pass
    plt.title('N={}'.format(np.sum(neuron_keep)))

plt.xlabel('')
plt.suptitle('V4 by Ch')
plt.savefig('./temp_figs/PSTH_V4_by_ch_{}_{}.pdf'.format(block_type, signal_type))
plt.savefig('./temp_figs/PSTH_V4_by_ch_{}_{}.png'.format(block_type, signal_type))




""" temp """

""" below are legancy script """

def GetDataCat( list_data_groupave, list_ts, list_signal_info, list_cdtn ):
    return [np.dstack(list_data_groupave), list_ts[0], np.concatenate(list_signal_info), list_cdtn[0]]

[data_groupave, ts, signal_info, cdtn] = GetDataCat( list_data_groupave, list_ts, list_signal_info, list_cdtn )


colors = np.vstack([pnp.gen_distinct_colors(3, luminance=0.9), pnp.gen_distinct_colors(3, luminance=0.6)])
linestyles = ['-', '-', '-', '--', '--', '--']
[h_fig, h_ax]=plt.subplots(nrows=1, ncols=2, sharex=True, sharey=True, figsize=[12,6])
plt.axes(h_ax[0])
psth = pna.SmoothTrace(np.mean(data_groupave[:,:,signal_info['channel_index']<=32], axis=2), ts=ts, sk_std=0.007, axis=1)
for i in range(psth.shape[0]):
    plt.plot( ts, psth[i,:], color=colors[i], linestyle=linestyles[i])
plt.title('V4')
plt.xlabel('t (s)')
plt.ylabel('spk/sec')

plt.axes(h_ax[1])
psth = pna.SmoothTrace(np.mean(data_groupave[:,:,signal_info['channel_index']>32], axis=2), ts=ts, sk_std=0.007, axis=1)
for i in range(psth.shape[0]):
    plt.plot( ts, psth[i,:], color=colors[i], linestyle=linestyles[i])
plt.legend(cdtn)
plt.title('IT')

plt.suptitle('firing rate, average over all session & all neurons')
plt.savefig('/shared/homes/sguan/Coding_Projects/support_data/GroupAve_srv_mask.pdf')



[h_fig, h_ax]=plt.subplots(nrows=4, ncols=4, sharex=True, sharey=True, figsize=[10,8])
h_ax = np.ravel(h_ax)
for i, l in enumerate(range(-8,8)):
    plt.axes(h_ax[i])
    neuron_keep = (signal_info['channel_index'] > 32) * (signal_info['area']=='TEm') * (np.abs(signal_info['depth']-l)<=laminar_range_ave)
    if np.sum(neuron_keep)>0:
        psth = pna.SmoothTrace(np.mean(data_groupave[:, :, neuron_keep], axis=2), ts=ts, sk_std=sk_std, axis=1)
        for i in range(psth.shape[0]):
            plt.plot(ts, psth[i, :], color=colors[i], linestyle=linestyles[i], alpha=alphas[i])
        plt.title('depth={}, N={}'.format(l, np.sum(neuron_keep)))
        plt.ylabel(ylabel)
plt.legend(cdtn)
plt.xlabel('t (s)')
plt.suptitle('STS by depth {} {}'.format(block_type, signal_type))
plt.savefig('./temp_figs/PSTH_STS_by_depth_{}_{}_{}.pdf'.format(block_type, signal_type, plot_highlight))
plt.savefig('./temp_figs/PSTH_STS_by_depth_{}_{}_{}.png'.format(block_type, signal_type, plot_highlight))


# plot depth profile in one panel
scale_depth=50
[h_fig, h_ax]=plt.subplots(nrows=1, ncols=6, sharex=True, sharey=True, figsize=[10,8])
for l in range(-8,9,2):
    neuron_keep = (signal_info['channel_index'] > 32) * (signal_info['area']=='TEm') * (np.abs(signal_info['depth']-l)<=laminar_range_ave)
    if np.sum(neuron_keep)>0:
        psth = pna.SmoothTrace(np.mean(data_groupave[:, :, neuron_keep], axis=2), ts=ts, sk_std=sk_std, axis=1)
        for j in range(6):
            plt.axes(h_ax[j])
            if j==0:
                plt.title('all')
                alphas = [1, 1, 1, 1, 1, 1]
            elif j==1:
                plt.title('nov')
                alphas = [1, 1, 1, 0, 0, 0]
            elif j == 2:
                plt.title('fam')
                alphas = [0, 0, 0, 1, 1, 1]
            elif j==3:
                plt.title('noise 0%')
                alphas = [1, 0, 0, 1, 0, 0]
            elif j==4:
                plt.title('noise 50%')
                alphas = [0, 1, 0, 0, 1, 0]
            elif j==5:
                plt.title('noise 70%')
                alphas = [0, 0, 1, 0, 0, 1]
            for i in range(psth.shape[0]):
                plt.plot(ts, psth[i, :]+scale_depth*l, color=colors[i], linestyle=linestyles[i], alpha=alphas[i])
            # plt.ylabel(ylabel)
plt.xticks([-0.1,0,0.1,0.2,0.3,0.4,0.5], ['','0','','0.2','','0.4',''])
plt.suptitle('STS by depth')
plt.savefig('./temp_figs/PSTH_STS_by_depth_{}_{}.pdf'.format(block_type, signal_type))
plt.savefig('./temp_figs/PSTH_STS_by_depth_{}_{}.png'.format(block_type, signal_type))




""" V4 by RF location: fovea vs peripheral """

plot_highlight = ''
if plot_highlight == 'nov':
    alphas = [1,1,1,0,0,0]
    alphas_p = [0, 0, 0, 1, 0]
elif plot_highlight == 'fam':
    alphas = [0,0,0,1,1,1]
    alphas_p = [0, 0, 0, 0, 1]
elif plot_highlight == '00':
    alphas = [1,0,0,1,0,0]
    alphas_p = [1, 0, 0, 0, 0]
elif plot_highlight == '50':
    alphas = [0,1,0,0,1,0]
    alphas_p = [0, 1, 0, 0, 0]
elif plot_highlight == '70':
    alphas = [0,0,1,0,0,1]
    alphas_p = [0, 0, 1, 0, 0]
elif plot_highlight == '':
    alphas = [1, 1, 1, 1, 1, 1]
    alphas_p = [1, 1, 1, 1, 1]
else:
    alphas = [1, 1, 1, 1, 1, 1]
    alphas_p = [1, 1, 1, 1, 1]

def plot_psth_p(neuron_keep):
    N_neuron = np.sum(neuron_keep)
    [psth_mean, psth_std, data_norm] = cal_spth_std(neuron_keep)
    p_values = t_test_score(data_norm)
    for i in range(psth_mean.shape[0]):
        plt.plot(ts, psth_mean[i, :], color=colors[i], linestyle=linestyles[i], alpha=alphas[i])
        plt.fill_between(ts, psth_mean[i, :] - psth_std[i, :] / np.sqrt(N_neuron),
                         psth_mean[i, :] + psth_std[i, :] / np.sqrt(N_neuron), color=colors[i], alpha=0.2*alphas[i])
    plt.xlabel('t (s)')
    plt.ylabel(ylabel)
    for i, p in enumerate(p_values):
        plt.plot(ts[p < p_thrhd], 0.5-(i + 1) * 0.1 * np.ones(np.sum(p < p_thrhd)), '.', color=colors_p[i], alpha=alphas_p[i])

list_chan_fov = [1,2,3,4,6,7,8,11,12,17,18]
list_chan_per = [5,9,10,15,16,20,21,22,25,26,28,32]

[h_fig, h_ax]=plt.subplots(nrows=1, ncols=2, sharex=True, sharey=True, figsize=[12,5])
p_thrhd = 0.05

plt.axes(h_ax[0])
neuron_keep = ( np.in1d(signal_info['channel_index'], list_chan_fov))
plot_psth_p(neuron_keep)
plt.title('V4 fovea, N={}'.format(np.sum(neuron_keep)))

plt.axes(h_ax[1])
neuron_keep = ( np.in1d(signal_info['channel_index'], list_chan_per))
plot_psth_p(neuron_keep)
plt.title('V4 periphral, N={}'.format(np.sum(neuron_keep)))

plt.suptitle('V4 by RF')
plt.savefig('./temp_figs/PSTH_V4_by_RF_{}_{}.pdf'.format(block_type, signal_type))
plt.savefig('./temp_figs/PSTH_V4_by_RF_{}_{}.png'.format(block_type, signal_type))



[h_fig, h_ax]=pnp.create_array_layout_subplots(layout_GM32, tf_linear_indx=True)
h_fig.set_size_inches([10, 9], forward=True)
plt.tight_layout(pad=0.05)
for ch in range(1,32+1):
    plt.axes(h_ax[ch-1])
    neuron_keep = ( signal_info['channel_index']==ch)
    try:
        plot_psth_p(neuron_keep)
    except:
        pass
    plt.title('N={}'.format(np.sum(neuron_keep)))

plt.xlabel('')
plt.suptitle('V4 by Ch')
plt.savefig('./temp_figs/PSTH_V4_by_ch_{}_{}.pdf'.format(block_type, signal_type))
plt.savefig('./temp_figs/PSTH_V4_by_ch_{}_{}.png'.format(block_type, signal_type))