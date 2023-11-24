import requests, json, os, time
from EdgeGPT.EdgeUtils import Query, Cookie
from pathlib import Path

os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"

def get_Bing_response(query):
    q = Query(query, style="balanced", simplify_response=True, cookie_files="./bing_cookies_1.json")
    return {"text": q.output, "sources": q.sources_dict}

def protected_write(file, data):
    if not os.path.exists(file): # 防止要写入的文件不存在
        with open(file, "w+", encoding="utf-8") as f:
            f.write("{}") 
    old_json = {}
    with open(file, "r+", encoding="utf-8") as f:
        old_json = json.load(f)
        old_json.update(data)
    new_json = sorted(old_json.items(), key=lambda x: int(x[0]))
    with open(file, "w+", encoding="utf-8") as f:
        json.dump(dict(new_json), f, ensure_ascii=False, indent=4)

"""
为了防止网络问题，采用生成一条数据就写一条数据的方法
写数据的函数会先读取原来的数据，然后将新的数据加入到原来的数据中，然后再写入，防止网络波动导致的数据丢失
"""
def Bing_job(file_read, file_write):
    with open(file_read, "r") as f:
        data = json.load(f)
        for index in data:
            # if int(index) <= 4:
            #     continue
            content = data[index]
            for key in content.keys():
                if key == "origin_input":
                    continue
                content_for_method = content[key]
                # finish declare job
                declare_q = content_for_method["declare_input"]
                decalre_a = get_Bing_response(declare_q)
                print(decalre_a)
                content[key]["declare_ans"]["Bing"] = decalre_a
                # finish question job
                question_q = content_for_method["question_input"]
                question_a = get_Bing_response(question_q)
                content[key]["question_ans"]["Bing"] = question_a
                time.sleep(1)
            protected_write(file_write, {index: content})

files_list = ["en_part1.json", "en_part2.json"]

if __name__ == "__main__":
    for file in files_list:
        file_w = file.split(".")[0] + "_Bing.json"
        Bing_job(file, file_w)
        