import re

with open('docs/handoffs/app-modular-redesign.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update current status
text = re.sub(
    r"- 当前状态：.*?\n",
    "- 当前状态：已全量落地地图缩放分级自适应 LOD 渲染系统（彻底解决地图缩小后每个地名标签过大过乱、相互遮挡堆叠的问题，实现全景微光星座圆点、中景紧凑单行地名、近景展开完整标高的三态平滑演进）\n",
    text
)

# 2. Add Item 17 before ## 3. 关键决策
item17 = """17. **地图缩放分级自适应 LOD 渲染与地名标签净化（反馈联动落地）**：
    - **查明真机地名标签杂乱拥挤根因**：
      - 原 Marker 渲染逻辑对所有 50 座山峰在任何 Zoom 层级均统一展示两行制大胶囊（山峰名 + 海拔标高数据 + 呼吸点 + 下垂线），单个卡片宽度达 75~95px；
      - 当用户缩小地图进行全景浏览（如 Zoom < 8.2）时，川西 50 座山峰点位在 400px 屏幕上距离极近，50 个大号黑底胶囊严重碰撞堆叠成一团乱麻，彻底遮盖了底图瓦片与等高线地貌；
    - **构建三级自适应显示架构 (LOD - Level of Detail)**：
      - **全景远景视图 (Zoom < 8.2)**：
        - 未选中的山峰自动收敛为极简优雅的「极光微光星座圆标（Beacon Dots）」，带有 8px 实体核心点与微光呼吸光晕，大号胶囊 100% 自动消除，黑曜石暗夜地形一览无余；
        - 提供 32px × 32px 的大尺寸舒适触控热区（`p-3 -m-3`），支持鼠标悬停浮动微气泡预览，轻触任意圆点瞬时选中并平滑对齐；
        - **选中的山峰（如达瓦更扎）全层级保持完整 Hero Pin 展开**，用户永远不会丢失当前焦点；
      - **中景整洁视图 (8.2 <= Zoom < 9.5，含默认 Z9.0)**：
        - 隐藏冗余的标高副标题（`{{ m.alt }}m`），精简为单行紧凑地名胶囊（`text-[10px]`，内边距 `px-2 py-0.5`），卡片面积骤降 55%，50 座山峰排列整洁有序；
      - **近景探索视图 (Zoom >= 9.5)**：
        - 自动展开完整的地名、海拔数据与拓扑下垂线，满足徒步路线细节研究需求；
    - **自动化与视觉验证**：
      - 编写 Playwright 脚本 `scratch/verify_adaptive_map_lod.py`，移动端 400x757 视口实测全景 Z6.0、中景 Z9.0 与近景 Z14.0，生成三阶对比验证图 `map_lod_compact_z9.png`、`map_lod_minimal_z75.png`、`map_lod_detailed_z10.png`，自测 100% PASS。

"""

if "17. **地图缩放分级自适应 LOD 渲染与地名标签净化" not in text:
    text = text.replace("## 3. 关键决策", item17 + "## 3. 关键决策")

# 3. Add test result
test_line = "- `python scratch/verify_adaptive_map_lod.py`: PASS (全景微光圆点、中景紧凑单行、近景标高展开自适应验证 100% 通过)\n"
if "verify_adaptive_map_lod.py" not in text:
    text = text.replace(
        "- `python scripts/package_deploy.py`: PASS",
        test_line + "- `python scripts/package_deploy.py`: PASS"
    )

with open('docs/handoffs/app-modular-redesign.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Handoff document updated successfully with Item 17")
