# 提示词与验收

## 组装生成任务

先列不变量，再写本轮变化；不要仅靠“保持不变”一句话。以下为可改写模板，不是必须逐字执行的工具指令。

```text
Task: [single typography edit / comparative wedding table-number concepts].
Reference roles: Image 1 is the immutable original frame; Image 2, if present,
supplies ONLY the selected insert finish and typography context.
Preserve: [outer shape, proportions, border width, finish, inner opening,
ornament count and exact positions]. No added motifs, no frame redesign.
Change only: [explicit authorized variables].
Exact insert text: [TABLE + requested number].
Typography: [visible letterform characteristics, optical scale, placement,
ink color, manufacturing appearance if requested].
Material: [opaque/reflective/translucent, surface texture and color].
Comparison controls: same frame, optical numeral height, camera, lighting,
background and every non-varied property across panels.
Layout: [one image / 2x2 / 3x2], full products visible; option labels outside
the insert, no extra brand text, decoration, dimensions or factory claims.
For finishing studies: accurate restrained edge detail; macro matches main view.
```

镜面描述包含“真实反射”和“安静场景”；不要通过变成不透明板解决反光。单图换字保留原背景、构图与反射，不自动重新布置婚礼场景。

边框例子只作观察方法：绳结款核对绳圈厚度和结形；折面款核对棱面及轮廓；蝴蝶款按当前图点数并记录位置。不要把某张历史图的装饰数量套用到其他产品。

## 最终图检查

- 边框：与原图并排看外轮廓、开口比例、纹理、厚度、颜色、装饰数量和位置。显著漂移应修正，不能只在文案里宣布不变。
- 内容：桌号正确、无残留品牌标签，`TABLE` 等文字无错字，没有新增姓名日期或未经请求的装饰。
- 对比：各款字形确有差异；只有允许的变量发生变化；两位数没有顶到边框；宏观和局部一致。
- 材质：镜面仍有反射；不透光底材没有被渲成透明；涂层未冒充厚贴字；工艺夸张部分应修正或明确限定。
- 交付：图片实际可见，最终保存文件存在且可读取。原图与旧版本未覆盖。

如果本轮要求精确保留原像素，生成图的近似一致不足以通过；说明限制，并在用户明确要求允许的精确编辑方式下处理，不偷偷切换工具或把近似结果标记为严格保形成功。

## 验收场景（用于检查 Skill 决策，不强制付费生成）

1. 用户上传烟灰镜面桌牌说“换下字体”：只改字形，不改白色字、镜面、边框、场景；没有必要先要求选字体名。
2. 用户随后说“再来些”：沿用当前维度生成有区别的候选，不能重启材质探索。
3. 用户纠正“边框不能修改”：废止此前改框方向，重新使用原框参考，不继续减细。
4. 用户说“都不错”：保留候选；不记录生产批准，不擅自缩减成三款。
5. 会话中上传新蝴蝶框：按新框观察装饰，不继承上一款绳结；无会话上下文时不武断推定用途。
6. 用户说“这个字体给工厂”：不能提供虚构字体名；找到真实字库并核对使用许可、渲染和尺寸条件后才准备可生产文件。
