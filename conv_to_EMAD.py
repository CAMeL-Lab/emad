from copy import deepcopy

from tools import driver, parse_tag
import EMAD

def convert(input_tag, map_driver):

    #Parse input tag into feat_val dict (using FSTs)
    feat_val_dicts = parse_tag.parse(input_tag, map_driver)
    #print(feat_val_dicts)
    output_tags = []
    #convert the features using the pandas df
    for fv_dict in feat_val_dicts:
        output_tags = output_tags + convertFeats(fv_dict, map_driver)

    #convert the features into the output tag (using FSTS? and maybe another input format)
    output_tags = make_uniqe(output_tags)

    for tag in output_tags:
        tag.addDefaults()

    return output_tags

def make_uniqe(tags):
    new_tags = []
    for tag in tags:
        if tag not in new_tags:
            new_tags.append(tag)

    return new_tags

def convertFeats(feat_val_dict, map_driver):
    output_tags = [EMAD.Tag()]
    map_table = map_driver['map']
    
    for feat, val in feat_val_dict.items():
        matching_rows = map_table[(map_table['feat'] == feat) & (map_table['val'] == val)]
        #print(feat, val)
        #print(matching_rows)
        subtags = convert_rows_to_subtags(matching_rows)
        #print("here", subtags)
        if subtags != {}:
            output_tags = add_subtag_to_output(output_tags, subtags)
            #print(output_tags)
    
    #for tag in output_tags:
    #    tag.addDefaults()

    return output_tags

def convert_rows_to_subtags(map_rows):
    subtags = {}
    for index, row in map_rows.iterrows():
        subtag = {}
        for EMAD_feat in EMAD.FEATURES:
            value = row[EMAD_feat]
            if value != '-':
                subtag[EMAD_feat] = value
        
        EMAD_cat = row['EMAD_cat']

        if EMAD_cat not in subtags.keys():
            subtags[EMAD_cat] = []
        subtags[EMAD_cat].append(subtag)
    
    return subtags

def add_subtag_to_output(output_tags, subtags):
    #print(output_tags)
    new_output_tags = []
    for tag in output_tags:
        for EMAD_cat, subtags_list in subtags.items():
            for subtag in subtags_list:
                curr_tag = deepcopy(tag)
                for feat, val in subtag.items():
                    if val != "-1":
                    
                        if not curr_tag[EMAD_cat]:
                            curr_tag[EMAD_cat] = EMAD.Subtag()

                        curr_tag[EMAD_cat][feat] = val
                
                if curr_tag not in new_output_tags:        
                    new_output_tags.append(curr_tag)

    #print(len(output_tags), len(new_output_tags))
    output_tags = deepcopy(new_output_tags)

    #print(len(output_tags))
    return output_tags

if __name__ == "__main__":
    tagset = "MADA"
    #input_tag = "diac:wawAsiTatahum lex:wAsiTap pos:noun prc3:0 prc2:wa_conj prc1:0 prc0:0 per:na asp:na vox:na mod:na gen:f fgen:f num:s fnum:s stt:c cas:a enc0:3mp_poss rat:i"
    input_tag = "pos:noun prc3:0 prc2:0 prc1:0 prc0:0 per:na asp:na vox:na mod:na form_gen:m gen:f form_num:s num:p stt:d cas:n enc0:0 rat:i"
    input_tag = "pos:part_verb prc3:0 prc2:0 prc1:la_emph prc0:na per:na asp:na vox:na mod:na form_gen:na gen:na form_num:na num:na stt:na cas:na enc0:0 rat:na"
    
    #tagset = "CATiB6"
    #input_tag = "VRB-PASS"

    #tagset = "CAMeL"
    #input_tag = "PART+ADJ.MS+PRON"

    #tagset = "BW"
    #input_tag = "IV3MP+IV+IVSUFF_SUBJ:MP_MOOD:SJ"

    map_driver = driver.setup_driver(tagset)

    #print(list(map_driver['map'][map_driver['map']['feat']=='GEN']['val']))
    #x = parse_tag.make_fst(map_driver)
    
    output_tags = convert(input_tag, map_driver)
    for tag in output_tags:
        print(tag)
        print([tag])

    print(len(output_tags))