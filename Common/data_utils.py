# coding: utf-8
'''
Some utility functions for loading up, investigating, and analysing
the corpora that we use.
'''
from __future__ import division
import os
import pandas as pd
import numpy as np


def visgenid_to_coco_id(df, vi):
    # works for example on visgen_regdf
    return df[df['image_id'] == vi]['coco_id']


def load_dfs(path, inlist):
    df = dict()
    for this_df in inlist:
        df[this_df] = pd.read_json(os.path.join(path, this_df + '.json.gz'),
                                   typ='frame', orient='split',
                                   compression='gzip')
    return df


def get_obj_key(df, obj_id, key='bb'):
    return df[df['obj_id'] == obj_id][key].values[0]


def get_obj_bb(df, obj_id):
    return get_obj_key(df, obj_id, key='bb')


def get_rel_type(df, rel_id):
    return tuple(df[df['rel_id'] == rel_id]['sub_syn rel_syn obj_syn'.split()].values[0])


def get_rel_instances(reldf, rel, op):
    '''Get instances of relations fitting the description.

    Parameters:
    rel - the target relation, as triple (subj_syn, rel_syn, obj_syn)
    op  - the comparison operator for each position (e.g., == or !=)'''
    query_string = []
    for key, val, op in zip(['sub', 'rel', 'obj'], rel, op):
        if val != '*':
            query_string.append('({key}_syn {op} "{val}")'.format(key=key, op=op, val=val))
    return reldf.query(' & '.join(query_string))


def plot_rel_by_relid(rel_df, obj_df, rel_id):
    columns = 'image_id sub_id obj_id sub_syn rel_syn predicate obj_syn'.split()
    (ii, sub_id, obj_id, sub_syn, rel_syn, predicate, obj_syn) = \
        rel_df[rel_df['rel_id'] == rel_id][columns].values[0]

    subj_bb = get_obj_bb(obj_df, sub_id)
    obj_bb = get_obj_bb(obj_df, obj_id)

    return ii, [(subj_bb, (str(sub_id), 'b')),
                (obj_bb, (str(obj_id), 'g'))]


# some functions for computing relations between objects in visgen
#  TODO: should be generalised.. there is too much overlap in functionality
def center_point(bb):
    x, y, w, h = bb
    return x+w/2, y+h/2


def point_distance(xa, ya, xb, yb):
    return np.sqrt((xb-xa)**2 + (yb-ya)**2)


def compute_distance_objs(imgdf, objdf, ii, si, oi):
    cs = center_point(get_obj_bb(objdf, si))
    co = center_point(get_obj_bb(objdf, oi))
    dist = point_distance(*cs, *co)
    iw, ih = imgdf[imgdf['image_id'] == ii][['width', 'height']].values[0]
    img_diag = point_distance(0, iw, iw, ih)
    return dist / img_diag


def compute_distance_relargs_row(imgdf, objdf, relrow):
    return compute_distance_objs(imgdf, objdf, relrow['image_id'],
                                 relrow['sub_id'], relrow['obj_id'])


def compute_relpos_relargs_row(imgdf, objdf, relrow):
    return compute_relpos_objs(imgdf, objdf, relrow['image_id'],
                               relrow['sub_id'], relrow['obj_id'])


def compute_relpos_objs(imgdf, objdf, ii, si, oi):
    xs, ys = center_point(get_obj_bb(objdf, si))
    xo, yo = center_point(get_obj_bb(objdf, oi))
    iw, ih = imgdf[imgdf['image_id'] == ii][['width', 'height']].values[0]
    img_diag = point_distance(0, iw, iw, ih)
    xr = (xs - xo) / img_diag
    yr = (ys - yo) * -1 / img_diag
    return xr, yr


def compute_obj_sizes(imgdf, objdf, ii, si, oi):
    iw, ih = imgdf[imgdf['image_id'] == ii][['width', 'height']].values[0]
    area_i = iw * ih

    xs, ys, ws, hs = get_obj_bb(objdf, si)
    area_s = (xs+ws) * (ys+hs) / area_i
    xo, yo, wo, ho = get_obj_bb(objdf, oi)
    area_o = (xo+wo) * (yo+ho) / area_i

    return area_s, area_o


def compute_obj_sizes_row(imgdf, objdf, relrow):
    return compute_obj_sizes(imgdf, objdf, relrow['image_id'],
                             relrow['sub_id'], relrow['obj_id'])


def get_all_predicate(reldf, predicate):
    return reldf[reldf['predicate'].str.lower().isin(predicate)]

    