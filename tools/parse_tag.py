from pyfoma import FST, Paradigm
import re

def cln_pyfoma_spcl_chrs(value):
    for i in "[]^$?*+()/|_:-":       # in case any regex chrs are in the values, expecially BW
        value = value.replace(i, f"\{i}")
    value = value.replace(".", "。")
    return value

def get_vals(feat, map_driver):
    vals = [cln_pyfoma_spcl_chrs(val) for val in
            map_driver['map'][map_driver['map']['feat'] == feat]['val']
    ]
    vals = "|".join(list(set(vals)))
    #print(vals)
    return vals

def make_fst_format(feats, tag_format):
    tag_format = tag_format.replace(":", "\:")
    tag_format = tag_format.replace(".", "。")
    tag_format = tag_format.replace("_", "\_")
    for feat in feats:
        tag_format = tag_format.replace(f"#{feat}#", f"${feat} ")
    
    #print(tag_format)
    return tag_format

def make_fst(map_driver):
    fsts = {}

    #print(map_driver)
    for feat in map_driver['features']:
        fsts[feat] = FST.re(f"'':'<{feat}>' ({get_vals(feat, map_driver)}) '':'<\/{feat}>'")
        #print(f"'':'<{feat}>' ({get_vals(feat, map_driver)}) '':'<\/{feat}>'")

    fst_format = make_fst_format(map_driver['features'], map_driver['format'])
    #print(fst_format)
    fst = FST.re(fst_format, fsts)
    return fst

def extract_feats(input_tag, map_driver):
    fst = map_driver['fst']
    #print(input_tag)
    try:
        x = Paradigm(fst, input_tag)
    except:
        print(f"ERROR in capturing tag: '{input_tag}'")
        return None
    #print(x)
    return x

def get_feat_val_dicts(parsed_tag, map_driver):
    feat_val_dict = {}
    for feat in map_driver['features']:
        if m := re.search(f"<{feat}>(?P<val>.*)</{feat}>", parsed_tag):
            feat_val_dict[feat] = m['val']
        else:
            feat_val_dict[feat] = '#NULL#'
    return feat_val_dict

def parse(input_tag, map_driver):
    dicts = []

    input_tag = cln_pyfoma_spcl_chrs(input_tag)
    parsed_tags = extract_feats(input_tag, map_driver)

    if parsed_tags:
        for tag in parsed_tags.para:
            tag = tag[2]
            #get_feat_val_dicts(tag, map_driver)
            dicts.append(get_feat_val_dicts(tag, map_driver))
    else:
        return []
    
    return dicts
'''
map = "CAMeL_to_EMADA"
input_tag = "PART+ADJ+PRON"
map_driver = read.read_map(map)
parse(input_tag, map_driver)
'''