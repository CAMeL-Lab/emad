import conv_from_EMAD, conv_to_EMAD, EMAD
from tools import driver, parse_tag

input_tagset = "CATiB6"
output_tagset = "BW"
mismatch_file = f"mismatch_log_{input_tagset}_{output_tagset}.txt"
error_file = f"error_log_{input_tagset}_{output_tagset}.txt"
logs_path = "./log"

def main():
    tags ={}

    input_map_driver = driver.setup_driver(input_tagset)
    output_map_driver = driver.setup_driver(output_tagset)

    memoize = {}

    with open("./data/parallel/uniq_data.par", "r") as f:
        count, true_count, error_count, false_count = 0, 0, 0, 0
        flag = False

        for count, line in enumerate(f):
            #print(line)

            tags["BW"], tags["MADA"], tags["CATiB6"] = split_line(line)

            if not tags[input_tagset] in memoize.keys():
                memoize[tags[input_tagset]] = convert(tags[input_tagset], input_map_driver, output_map_driver)
            output_tags = memoize[tags[input_tagset]]

            #print(output_tags)
            if output_tags is None or output_tags == []:
                error_count += 1
                with open(f"{logs_path}/{error_file}", 'a') as f:
                    f.write(f"Error in converting tag, no output was found: {tags[input_tagset]}\n")
            
            else:
                expected_parsed = parse_tag.parse(tags[output_tagset], output_map_driver)
                #print(bw_tag)
                #print(f"OUTPUT:\t{output_tags}")
                #print(f"EXPECTED:\t{expected_parsed}")
                flag = False
                for tag in output_tags:
                    #print(tag)
                    if output_matches(tag, expected_parsed):
                        true_count += 1
                        flag = True
                        #print("H")
                        break
                
                if not flag:
                    false_count += 1
                    log_conversion_error(tags[input_tagset], tags[output_tagset], expected_parsed, output_tags)

            if count % 10 == 9:
                print(count + 1)
                #print(tags["BW2"], tags["MADA"], tags["CATiB6"])
            
                
    print("Total number of tags converted:", count + 1)
    print("Number of tags that returned an output", true_count + false_count)
    print()
    print("Ratio of correct output", true_count / (true_count + false_count))
    print("Ratio of false output", false_count / (true_count + false_count))
    print(count + 1)
    print(true_count + false_count)
    print((true_count + false_count) / (count + 1))
    print(true_count / (true_count + false_count))
    print(false_count / (true_count + false_count))

    return

def split_line(line): # made to handle splitting the line esp if there is a "," in the bw tag
    if line.count(",") == 2:
        return line.strip().split(",")
    
    line = line.strip()
    comma_id = line.find(",", line.find(",") + 1)
    bw_tag = line[:comma_id]
    mada_tag, CATiB6_tag = line[comma_id+1:].split(",")
    return bw_tag, mada_tag, CATiB6_tag

def output_matches(output, expected):
    for feat, val_list in output.items():
        flag = False

        for val in val_list:
            for tag in expected:
                if feat in tag and tag[feat] != "#NULL#":

                    if tag[feat]==val or val == "#VAL#" or (tag[feat] in ['na', 'no'] and val in ['na', 'no']):
                        flag = True
                    
                    #TODO quick fix for MADA
                    if output_tagset == "MADA" and feat == "RAT" and tag[feat] in ['na', 'no', 'n'] and val in ['na', 'no', 'n']:
                        flag = True
                    # TODO quick fix for MADA, if the expected feature is u
                    # and the map is predicting a specific value for it then count it as true
                    if output_tagset == "MADA" and tag[feat]=='u' and val != 'na':
                        flag = True
                else:
                    flag = True
        
        if not flag:
            return False
    
    return True

def convert(input_tag, input_map_driver, output_map_driver):
    #input_tag = "Asm/NOUN+hA/POSS_PRON_3FS"

    #print(input_tag)
    intermediate_tags = conv_to_EMAD.convert(input_tag, input_map_driver)
    if intermediate_tags is None:
        return None
    if len(intermediate_tags) > 100:
        print(len(intermediate_tags))
    
    output_tags = []
    for tag in intermediate_tags:
        output = conv_from_EMAD.convert(tag, output_map_driver)
        if output != None:
            output_tags.append(output)
        else:
            return None
    if len(intermediate_tags) > 100:
        print("Done")
    #print(output_tags)
    return output_tags
    

def log_conversion_error(input_tag, expected_raw, expected_parsed, output_tags):
    with open(f"{logs_path}/{mismatch_file}", 'a') as f:
        f.write(f"Error in converting tag: {input_tag}\n")
        f.write(f"expected: {expected_raw}\n")
        
        f.write("feature")
        f.write("\t\texpected"*len(expected_parsed))
        f.write("\t\toutput"*len(output_tags))
        f.write("\n")

        feats = get_out_feats(expected_parsed, output_tags)

        for feat in feats:
            f.write(f"{feat}\t\t")
            for ex in expected_parsed:
                if feat in ex:
                    f.write(f"{ex[feat]}\t\t")
                else:
                    f.write("-\t\t")
            
            for out in output_tags:
                if feat in out:
                    f.write(f"{out[feat]}\t\t")
                else:
                    f.write("-\t\t")
            f.write("\n")
        f.write("----------------------------------------------\n")

def get_out_feats(expected_parsed, output_tags):
    feats = []
    for tag in output_tags:
        for feat in tag.keys():
            if feat not in feats:
                feats.append(feat)
    for tag in expected_parsed:
        for feat in tag.keys():
            if feat not in feats:
                feats.append(feat)
    
    return feats

if __name__ == "__main__":
    with open(f"{logs_path}/{mismatch_file}", "w") as f:
        pass
    with open(f"{logs_path}/{error_file}", "w") as f:
        pass
    main()