import re
import pdb
import sys
import operator
import yaml
import argparse

def load_class(class_name, pp_file_name):
  class_start = re.compile("class\s+{0}\s*\(".format(class_name))
  class_end = ")"

  pp_file = open(pp_file_name)
  parse_line = ""
  class_found = False
  parsed_class = dict()

  for line in pp_file:
    if class_end in line:
      class_found = False
    if class_found and not re.sub("\s", "", line).startswith("#"):
      parse_line += line
    if class_start.search(line):
      class_found = True

  for line in parse_line.split(",\n"):
    pval = re.sub("\s", "", line.rstrip()).split("=")
    if pval[0] and pval[1]:
      param = pval[0]
      val = pval[1]
      parsed_class[param] = val

  pp_file.close()

  return parsed_class

def merge_class(class1, class2, replace_val = True):
  merged_class = dict(class2)
  for param, val in class1.iteritems():
    if replace_val:
      merged_class[param] = val
    else:
      merge_class.setdefault(param, val)
  return merged_class

def diff_class(class1, class2, only_params = False):
  diff = dict()
  for param, val in class1.iteritems():
    if not class2.has_key(param):
      diff[param] = val
    else:
      if class2[param] != val and not only_params:
        diff[param] = val
  return diff

def same_class(class1, class2, only_params = True):
  same = dict()
  for param, val in class1.iteritems():
    if class2.has_key(param):
      if only_params:
        same[param] = val
      else:
        if class2[param] == val:
          same[param] = val
  return same

def sync_classes(old_class, new_class, general_class):
  diff_old_new = diff_class(general_class, old_class, True)
  general_diff = diff_class(general_class, diff_old_new, True)
  return merge_class(general_diff, new_class)

def generate_output(out_class, out_name):
  new_pp = open(out_name, "w+")

  if out_class:
    max_key_len = max([len(param) for param in out_class.keys()])
    new_pp.write("class Processed (\n")
    for param, val in sorted(out_class.items(), key=operator.itemgetter(0)):
      new_pp.write("  {0}".format(param))
      new_pp.write(" " * (max_key_len - len(param) + 1))
      new_pp.write("= {0},\n".format(val))
    new_pp.write(")")

  new_pp.close()

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-c', '--config', dest='config', help='Configuration YAML')
  args = parser.parse_args()

  conf = open(args.config, 'r')
  tempConf = yaml.load_all(conf)

  for line in tempConf:
    first_file_name = line["FirstFileName"]
    second_file_name = line["SecondFileName"]
    third_file_name = line["ThirdFileName"]
    first_class_name = line["FirstClassName"]
    second_class_name = line["SecondClassName"]
    third_class_name = line["ThirdClassName"]
    actions_to_do = line["ActionsToDo"]

    replace_on_merge = line["ReplaceOnMerge"]
    diff_only_param_names = line["DiffOnlyParamNames"]
    same_only_param_names = line["SameOnlyParamNames"]

  #pdb.set_trace()
  try:
    first_class = load_class(first_class_name, first_file_name)
    second_class = load_class(second_class_name, second_file_name)
  except (IndexError, IOError):
    print "Please, specify classes with them files in config.yaml"
    raise SystemExit

  if "merge" in actions_to_do:
    merged_class = merge_class(first_class, second_class, replace_on_merge)
    generate_output(merged_class, "merged {0} with {1}.pp".format(first_class_name, second_class_name))
  if "diff" in actions_to_do:
    differ_class = diff_class(first_class, second_class, diff_only_param_names)
    generate_output(differ_class, "diff {0} with {1}.pp".format(first_class_name, second_class_name))
  if "same" in actions_to_do:
    same_class_fields = same_class(first_class, second_class, same_only_param_names)
    generate_output(differ_class, "same {0} with {1}.pp".format(first_class_name, second_class_name))
  if "sync" in actions_to_do:
    try:
      third_class = load_class(third_class_name, third_file_name)
    except (IndexError, IOError):
      print "Please, specify classes with them files in config.yaml"
      raise SystemExit
    synced = sync_classes(first_class, second_class, third_class)
    generate_output(synced, "sync {0} and {1} in {2}.pp".format(first_class_name, second_class_name, third_class_name))


if __name__ == '__main__':
  main()