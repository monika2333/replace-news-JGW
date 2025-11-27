# 文本处理脚本说明

本仓库收录了一组用于清洗、重排、编号与合并新闻文本的脚本，均基于 Python 3.8+。

## bulk_replace.py
清洗指定目录下的 `.txt` 文件，做常见格式规范化。
- 去掉前缀“来源：”
- 英文括号 `()` 统一成中文括号 `（）`
- 清除括号前的多余空格
- 将“客户端/客户端.”统一为“客户端”
- 将“微信公众号/官方账号.”统一为“微信公众号”
- 去掉“新华社记者报道/报道”等冗余字样

**使用：**
```bash
python bulk_replace.py            # 清洗当前目录及子目录
python bulk_replace.py <目录>     # 指定目标目录
python bulk_replace.py --dry-run  # 仅预览修改
```

## reorder_brief.py
按照固定优先级（委->省->市->学校等）重排简报中的条目。
- 自动按标题/编号切分条目
- 依据关键词匹配分组并排序
- 支持写回原文件或输出新文件

**使用：**
```bash
python reorder_brief.py <文件>
```
可选参数：`--output <文件>` 指定输出路径；`--in-place` 直接覆盖原文件。

## add_numbers.py
为文本中的条目自动添加递增编号。
- 识别条目并按顺序编号
- 支持多种编号分隔符，避免重复编号
- 可指定单个文件或目录

**使用：**
```bash
python add_numbers.py                 # 处理当前目录下的 .txt
python add_numbers.py <文件或目录>
```

## merge_summaries.py
合并分段的高分摘要文件 `high_score_summaries_YYYY_MM_DD(n).txt`。
- 仅保留四类分类标题：`【京内正面】【京内负面】【京外正面】【京外负面】`
- 先读取已存在的合并文件，在原有内容上去重追加
- 默认合并成功后删除分段文件，可选择保留

**使用：**
```bash
python merge_summaries.py                        # 扫描当前目录并合并，输出 *_merged.txt
python merge_summaries.py --keep-sources         # 合并后保留分段文件
python merge_summaries.py --root <目录>          # 指定扫描目录
python merge_summaries.py --suffix <后缀>        # 调整合并文件的后缀，默认 _merged
```
