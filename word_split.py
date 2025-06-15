from docx import Document
import FILe_reader


def sim_str(str1, str2):
    if abs(len(str1) - len(str2))>8:
        return False
    word_list = []
    for word_a in str1: 
        if word_a in str2:
            word_list.append(word_a)
    select_num = 0
    score = 0
    if len(word_list) > 0:
        for word_b in str2:
            if select_num == len(word_list):
                break
            if word_b == word_list[select_num]:
                score += 1
                select_num += 1
    if score >= 0.6 * len(str1):
        return True
    return False


# Transform dict to list When document have style
def transform_dict_to_list(layer:dict, k:str=0, res:list = []):
    if layer.get('content',True) and len(layer['content']) > 0:
        if len(layer['content']) > 1:
            for i in layer['content']:
                res.append((k, i, [False]))
        else:
            res.append((k, layer['content'][0], [False]))
    for k in layer.keys():
        if k not in ['content','max_layer']:
            res = transform_dict_to_list(layer[k], k, res)
    return res

# Find the first element of list
def find_first_element(Search_list, target_value, Select_num, Style=False):
    if sim_str(Search_list[Select_num][1][0], target_value):
        return Search_list[Select_num][0]
    return False


def text_to_chunking_with_header(docx_path, layer):
    # 打开.docx文件
    doc = Document(docx_path)
    
    layer_list = transform_dict_to_list(layer, 0, [])
    sorted_list = sorted(layer_list, key=lambda x: int(x[1][1]))
    chunk = []
    text = []
    Select_num = 0
    for paragraph in doc.paragraphs:
        text.append(paragraph.text+'\n')
        if Select_num < len(sorted_list) and find_first_element(sorted_list, paragraph.text, Select_num, True):
            Select_num += 1
            chunk.append(''.join(text))
            text = []
    chunk.append(''.join(text))
    
    if len(chunk)  < len(sorted_list)*0.5:
        return False
    return chunk


layer = FILe_reader.File_reader(r'.\FILE\test_e.docx')


print(len(text_to_chunking_with_header(r'.\FILE\test_e.docx', layer)))