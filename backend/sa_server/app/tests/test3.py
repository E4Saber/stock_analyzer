import logging
import os
import pickle
import time
import requests
import pandas as pd

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 全局变量
host = "https://data.stats.gov.cn/easyquery.htm"
tree_data_path = "./tree.data"
data_dir = "./data"

# 确保目录存在
os.makedirs(data_dir, exist_ok=True)

def get_tree_data(id="zb"):
    """
    递归获取树形菜单中的数据
    """
    r = requests.post(f"{host}?id={id}&dbcode=hgnd&wdcode=zb&m=getTree", verify=False)
    logging.info(f"访问URL: {r.url}")
    data = r.json()

    for node in data:
        if node["isParent"]:
            node["children"] = get_tree_data(node["id"])
        else:
            node["children"] = []

    return data

def init_tree():
    """
    初始化树形菜单数据并保存
    """
    data = get_tree_data()
    with open(tree_data_path, "wb") as f:
        pickle.dump(data, f)
    logging.info(f"树形菜单数据已保存到 {tree_data_path}")

def get_stat_data(sj, zb):
    """
    根据统计指标和时间获取数据
    """
    payload = {
        "dbcode": "hgnd",
        "rowcode": "zb",
        "m": "QueryData",
        "colcode": "sj",
        "wds": "[]",
        "dfwds": f'[{{"wdcode":"zb","valuecode":"{zb}"}},{{"wdcode":"sj","valuecode":"{sj}"}}]',
    }

    r = requests.get(host, params=payload, verify=False)
    logging.info(f"访问URL: {r.url}")
    time.sleep(2)  # 避免请求过快

    try:
        resp = r.json()
        if resp["returncode"] == 200:
            return resp["returndata"]
        else:
            logging.error(f"错误: {resp}")
            return None
    except Exception as e:
        logging.error(f"解析响应时出错: {e}")
        return None

def write_csv(node_id, sj):
    """
    将数据写入CSV文件
    """
    fp = os.path.join(data_dir, node_id + ".csv")
    # 文件是否存在，如果存在，不采集
    if os.path.exists(fp):
        logging.info(f"文件已存在: {fp}")
        return

    stat_data = get_stat_data(sj, node_id)
    if stat_data is None:
        logging.error(f"未找到数据: {node_id}")
        return

    # csv 数据
    csv_data = {"zb": [], "value": [], "sj": [], "zbCN": [], "sjCN": []}
    for node in stat_data["datanodes"]:
        csv_data["value"].append(node["data"]["data"])
        for wd in node["wds"]:
            csv_data[wd["wdcode"]].append(wd["valuecode"])

    # 指标编码含义
    zb_dict = {}
    sj_dict = {}
    for node in stat_data["wdnodes"]:
        if node["wdcode"] == "zb":
            for zb_node in node["nodes"]:
                zb_dict[zb_node["code"]] = {
                    "name": zb_node["name"],
                    "cname": zb_node["cname"],
                    "unit": zb_node["unit"],
                }

        if node["wdcode"] == "sj":
            for sj_node in node["nodes"]:
                sj_dict[sj_node["code"]] = {
                    "name": sj_node["name"],
                    "cname": sj_node["cname"],
                    "unit": sj_node["unit"],
                }

    # csv 数据中加入 zbCN 和 sjCN
    for zb in csv_data["zb"]:
        zb_cn = (
            zb_dict[zb]["cname"]
            if zb_dict[zb]["unit"] == ""
            else zb_dict[zb]["cname"] + "(" + zb_dict[zb]["unit"] + ")"
        )
        csv_data["zbCN"].append(zb_cn)

    for sj in csv_data["sj"]:
        csv_data["sjCN"].append(sj_dict[sj]["cname"])

    # 写入CSV文件
    df = pd.DataFrame(
        csv_data,
        columns=["sj", "sjCN", "zb", "zbCN", "value"],
    )
    df.to_csv(fp, index=False)
    logging.info(f"数据已保存到 {fp}")

def traverse_tree_data(nodes, sj):
    """
    遍历树形结构，对叶子节点获取数据
    """
    for node in nodes:
        # 叶子节点上获取数据
        if node["isParent"]:
            traverse_tree_data(node["children"], sj)
        else:
            write_csv(node["id"], sj)

def collect_data(sj="1978-"):
    """
    主函数：从树开始采集数据
    """
    # 检查树形菜单数据是否存在
    if not os.path.exists(tree_data_path):
        logging.info("树形菜单数据不存在，开始初始化...")
        init_tree()

    tree_data = []
    with open(tree_data_path, "rb") as f:
        tree_data = pickle.load(f)

    logging.info("开始遍历树形菜单并采集数据...")
    traverse_tree_data(tree_data, sj)
    logging.info("数据采集完成!")

def test_single_indicator(indicator_id, sj="1978-"):
    """
    测试单个指标的数据采集
    """
    logging.info(f"测试采集指标 {indicator_id} 的数据...")
    write_csv(indicator_id, sj)

if __name__ == "__main__":
    # 取消警告
    import warnings
    warnings.filterwarnings("ignore")
    
    # 测试模式：仅采集一个指标的数据
    # 这里使用的是文章中提到的某个指标ID，你可以替换成其他ID
    test_single_indicator("A0101", "2010-2020")
    
    # 全量模式：采集所有数据（谨慎使用，数据量大）
    # collect_data("2010-2020")