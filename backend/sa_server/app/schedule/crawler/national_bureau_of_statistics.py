import logging
import os
import pickle
import time
import requests
import json
import pandas as pd
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 全局变量
host = "https://data.stats.gov.cn/easyquery.htm"
tree_data_path = "./data/tree.data"
tree_data_path_json = "./data/tree_data.json"
data_dir = "./data"
indicators_map_path = "./data/indicators_map.json"

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
    return data

def view_tree_data():
    """查看tree.data的内容"""
    try:
        with open(tree_data_path, 'rb') as f:
            tree_data = pickle.load(f)
        
        # 为了更好的可读性，转为JSON格式输出
        # print(json.dumps(tree_data, ensure_ascii=False, indent=2))
        
        # 或者保存为JSON文件
        with open(tree_data_path_json, 'w', encoding='utf-8') as f:
            json.dump(tree_data, f, ensure_ascii=False, indent=2)
        print("已将tree.data转换为tree_data.json，可以使用JSON查看器查看")
    except Exception as e:
        print(f"无法读取tree.data: {e}")

def get_all_indicators(tree_data=None, parent_path="", indicators=None):
    """
    从树形结构中提取所有指标，包含层级结构
    """
    if indicators is None:
        indicators = {}
    
    if tree_data is None:
        if os.path.exists(tree_data_path):
            with open(tree_data_path, "rb") as f:
                tree_data = pickle.load(f)
        else:
            tree_data = init_tree()
    
    for node in tree_data:
        # 构建当前节点的路径
        current_path = f"{parent_path}/{node['name']}" if parent_path else node['name']
        
        # 保存节点信息
        indicators[node['id']] = {
            'id': node['id'],
            'name': node['name'],
            'path': current_path,
            'isParent': node['isParent']
        }
        
        # 继续递归处理子节点
        if node['children']:
            get_all_indicators(node['children'], current_path, indicators)
    
    return indicators

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

def fetch_data(node_id, sj, output_csv=True):
    """
    获取数据并返回DataFrame，同时可选是否保存CSV
    """
    fp = os.path.join(data_dir, node_id + ".csv")
    
    # 如果文件存在且需要CSV，直接读取已有文件
    if os.path.exists(fp) and output_csv:
        logging.info(f"文件已存在，读取: {fp}")
        return pd.read_csv(fp)
    
    stat_data = get_stat_data(sj, node_id)
    if stat_data is None:
        logging.error(f"未找到数据: {node_id}")
        return None

    # 处理数据
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

    # 创建DataFrame
    df = pd.DataFrame(
        csv_data,
        columns=["sj", "sjCN", "zb", "zbCN", "value"],
    )
    
    # 如果需要输出CSV
    if output_csv:
        df.to_csv(fp, index=False)
        logging.info(f"数据已保存到 {fp}")
    
    return df

def collect_data_by_category(category_id, sj="1978-", output_csv=True):
    """
    按类别收集数据
    """
    # 获取所有指标
    all_indicators = get_all_indicators()
    
    # 过滤属于该类别的指标
    category_indicators = {id: info for id, info in all_indicators.items() 
                          if id.startswith(category_id) and not info['isParent']}
    
    logging.info(f"找到 {len(category_indicators)} 个属于类别 {category_id} 的指标")
    
    # 收集数据
    results = {}
    for indicator_id, info in category_indicators.items():
        logging.info(f"正在获取指标 [{info['path']}] 的数据...")
        df = fetch_data(indicator_id, sj, output_csv)
        if df is not None:
            results[indicator_id] = {
                'info': info,
                'data': df
            }
    
    return results

def save_indicators_map():
    """
    保存所有指标的映射关系
    """
    all_indicators = get_all_indicators()
    
    # 按照层级结构整理
    structured_indicators = defaultdict(list)
    for id, info in all_indicators.items():
        parts = info['path'].split('/')
        if len(parts) == 1:  # 根级别
            structured_indicators['root'].append(info)
        else:
            parent = parts[0]
            structured_indicators[parent].append(info)
    
    # 保存为JSON文件
    import json
    with open(indicators_map_path, 'w', encoding='utf-8') as f:
        json.dump(structured_indicators, f, ensure_ascii=False, indent=4)
    
    logging.info(f"指标映射已保存到 {indicators_map_path}")
    return structured_indicators

def print_indicator_structure():
    """
    打印指标结构，方便查看
    """
    all_indicators = get_all_indicators()
    
    # 构建树形结构的字典
    tree_structure = {}
    for id, info in all_indicators.items():
        parts = info['path'].split('/')
        current = tree_structure
        for i, part in enumerate(parts):
            if part not in current:
                current[part] = {'__id__': id if i == len(parts)-1 else None}
            current = current[part]
    
    # 递归打印树
    def print_tree(node, level=0):
        for key, value in node.items():
            if key == '__id__':
                continue
            indent = '  ' * level
            node_id = value.get('__id__', '')
            node_id_str = f" [{node_id}]" if node_id else ''
            print(f"{indent}├─ {key}{node_id_str}")
            print_tree(value, level + 1)
    
    print("指标结构:")
    print_tree(tree_structure)

def main():
    """
    主函数
        
        - **初始化功能**: 获取并保存树形菜单结构
        ```bash
        python stats_crawler.py --init
        ```

        - **查看指标映射**: 生成所有指标的映射关系并以树形结构显示
        ```bash
        python stats_crawler.py --map
        ```

        - **按类别收集数据**: 例如收集行政区划类别(A01)的所有数据
        ```bash
        python stats_crawler.py --category A01 --years 2010-2022
        ```

        - **获取单个指标数据**: 获取单个指标的数据，同时返回DataFrame
        ```bash
        python stats_crawler.py --indicator A0101 --years 2010-2022
        ```

        - **只返回DataFrame不保存CSV**:
        ```bash
        python stats_crawler.py --indicator A0101 --no-csv
        ```
    """
    # 取消警告
    import warnings
    warnings.filterwarnings("ignore")
    
    # 命令行参数解析
    import argparse
    parser = argparse.ArgumentParser(description='国家统计局数据采集工具')
    parser.add_argument('--init', action='store_true', help='初始化树形菜单')
    parser.add_argument('--tree_to_json', action='store_true', help='查看JSON格式化树形菜单数据')
    parser.add_argument('--map', action='store_true', help='生成并显示指标映射')
    parser.add_argument('--category', type=str, help='按类别收集数据，例如 A0101')
    parser.add_argument('--indicator', type=str, help='获取单个指标的数据')
    parser.add_argument('--years', type=str, default='2010-2022', help='年份范围，例如 2010-2022')
    parser.add_argument('--no-csv', action='store_true', help='不输出CSV文件，仅返回DataFrame')
    args = parser.parse_args()
    
    # 执行对应操作
    if args.init:
        init_tree()
    
    if args.tree_to_json:
        view_tree_data()
        
    if args.map:
        save_indicators_map()
        print_indicator_structure()
        
    if args.category:
        results = collect_data_by_category(args.category, args.years, not args.no_csv)
        print(f"收集了 {len(results)} 个指标的数据")
        
    if args.indicator:
        df = fetch_data(args.indicator, args.years, not args.no_csv)
        if df is not None:
            print(f"指标 {args.indicator} 的数据:")
            print(df.head())
    
    # 如果没有指定任何操作，显示帮助
    if not (args.init or args.map or args.category or args.indicator):
        parser.print_help()

if __name__ == "__main__":
    main()