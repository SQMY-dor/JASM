import json
import os
import urllib.request
import urllib.error
import datetime

# 配置
API_URL = "https://api.dotgg.gg/cgfw/getgacha?game=endfield&type=characters"
IMAGE_BASE_URL = "https://static.dotgg.gg/endfield/characters/{}.webp"

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 设置输出目录为脚本的上级目录 (即 Endfield 文件夹)
OUTPUT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

IMAGES_DIR = os.path.join(OUTPUT_DIR, "Images", "Characters")
ELEMENTS_IMAGES_DIR = os.path.join(OUTPUT_DIR, "Images", "Elements")

def fetch_json(url):
    print(f"正在从 {url} 获取数据...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def download_image(url, save_path):
    print(f"正在下载图片 {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(save_path, 'wb') as f:
                f.write(response.read())
        print(f"已保存至 {save_path}")
    except Exception as e:
        print(f"下载失败 {url}: {e}")

def main():
    if not os.path.exists(IMAGES_DIR):
        print(f"创建目录 {IMAGES_DIR}")
        os.makedirs(IMAGES_DIR)

    if not os.path.exists(ELEMENTS_IMAGES_DIR):
        print(f"创建目录 {ELEMENTS_IMAGES_DIR}")
        os.makedirs(ELEMENTS_IMAGES_DIR)

    data = fetch_json(API_URL)
    
    characters_config = []
    factions_map = {} # factionId -> factionName
    elements_map = {} # elementInternalName -> elementName
    classes_map = {} # profession -> profession (名字作为ID)
    
    # 获取当前时间作为 ReleaseDate
    current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # 处理 API 返回的每个角色
    for char in data:
        try:
            char_id = char.get('id')
            codename = char.get('codename')
            name = char.get('name')
            
            # 如果缺少关键数据则跳过
            if not char_id or not codename or not name:
                print(f"跳过缺失数据的角色: {char}")
                continue

            rarity = int(char.get('rarity', 1))
            profession = char.get('profession', 'Unknown')
            
            # 处理元素
            element_internal = char.get('elementInternalName', 'None')
            element_name = char.get('elementName')
            if element_internal and element_name:
                elements_map[element_internal] = element_name
            
            # 处理职业
            if profession and profession != 'Unknown':
                classes_map[profession] = profession # 根据用户要求，使用名称作为InternalName
            
            # 处理势力 (Faction)
            faction_id = char.get('factionId')
            faction_name = char.get('faction')
            
            if faction_id and faction_name:
                factions_map[faction_id] = faction_name
                
            # 构建图片文件名
            image_filename = f"{char_id}.webp"
            
            # 检查 internalName 是否存在，否则使用 codename
            internal_name = char.get('codename')
            
            # 构建符合 JASM 架构的配置条目
            config_entry = {
                "Keys": [codename, name],
                "InternalName": internal_name,
                "DisplayName": name,
                "ReleaseDate": current_time, # 使用当前脚本运行时间
                "Image": image_filename,
                "Rarity": rarity,
                "Element": element_internal,
                "Class": profession,
                "Region": [faction_id] if faction_id else [],
                "ModFilesName": codename,
                "InGameSkins": []
            }
            
            characters_config.append(config_entry)
            
            # 如果图片不存在则下载
            image_save_path = os.path.join(IMAGES_DIR, image_filename)
            if not os.path.exists(image_save_path):
                 download_image(IMAGE_BASE_URL.format(char_id), image_save_path)
            else:
                pass 
                
        except Exception as e:
            print(f"处理角色 {char.get('name', 'Unknown')} 时出错: {e}")

    # 写入 characters.json
    output_chars = os.path.join(OUTPUT_DIR, "characters.json")
    print(f"正在写入角色配置到 {output_chars}...")
    with open(output_chars, 'w', encoding='utf-8') as f:
        json.dump(characters_config, f, indent=2, ensure_ascii=False)
        
    # 写入 regions.json
    regions_config = []
    for fid, fname in factions_map.items():
        regions_config.append({
            "InternalName": fid,
            "DisplayName": fname
        })
    output_regions = os.path.join(OUTPUT_DIR, "regions.json")
    print(f"正在写入地区配置到 {output_regions}...")
    with open(output_regions, 'w', encoding='utf-8') as f:
        json.dump(regions_config, f, indent=2, ensure_ascii=False)

    # 写入 elements.json
    elements_config = []
    for eid, ename in elements_map.items():
        elements_config.append({
            "InternalName": eid,
            "DisplayName": ename,
            "Image": f"{ename}.png" 
        })
    output_elements = os.path.join(OUTPUT_DIR, "elements.json")
    print(f"正在写入元素配置到 {output_elements}...")
    with open(output_elements, 'w', encoding='utf-8') as f:
        json.dump(elements_config, f, indent=2, ensure_ascii=False)

    # 写入 weaponClasses.json
    classes_config = []
    for cname in classes_map.keys():
        classes_config.append({
            "InternalName": cname,
            "DisplayName": cname
        })
    output_classes = os.path.join(OUTPUT_DIR, "weaponClasses.json")
    print(f"正在写入职业配置到 {output_classes}...")
    with open(output_classes, 'w', encoding='utf-8') as f:
        json.dump(classes_config, f, indent=2, ensure_ascii=False)

    # 写入 game.json (新增)
    game_config = {
      "GameName": "Arknights: Endfield",
      "GameShortName": "Endfield",
      "RarityName": "Rarity",
      "GameIcon": "Start_Game.png",
      "GameBananaUrl": "https://gamebanana.com/games/21842", 
      "GameModelImporterUrl": "",
      "GameModelImporterName": "",
      "GameModelImporterShortName": "",
      "GameModelImporterExeName": ['3DMigoto Loader.exe','Loader.exe','loader.exe']
    }
    output_game = os.path.join(OUTPUT_DIR, "game.json")
    print(f"正在写入游戏配置到 {output_game}...")
    with open(output_game, 'w', encoding='utf-8') as f:
        json.dump(game_config, f, indent=2, ensure_ascii=False)
        
    print(f"完成！共处理 {len(characters_config)} 个角色以及相关配置。")

if __name__ == "__main__":
    main()
