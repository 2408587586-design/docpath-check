# docpath-check

离线检查 Markdown 文档中的本地链接、图片路径和常见标题锚点，帮助开源项目在提交时发现失效引用。

不需要 API Key，不发起网络请求，无运行时第三方依赖。需要 Python 3.10 或更新版本。

## 使用

下载项目后，在终端执行：

```sh
python docpath.py 你的项目目录
```

也可以在本项目目录安装为命令：

```sh
python -m pip install .
docpath-check 你的项目目录
docpath-check 你的项目目录 --json
```

发现问题时会显示文件、行号、目标和原因。退出码 0 表示未发现问题，1 表示发现问题，2 表示命令参数错误。

## 第一版功能

- 检查行内链接和图片是否指向存在的路径。
- 支持相对路径、以项目根目录为起点的路径、URL 编码文件名。
- 检查常见 Markdown 标题锚点，支持中文和重复标题编号。
- 忽略代码围栏、简单行内代码、HTML 注释和外部网址。
- 提供 JSON 结果，便于接入自动化流程。
- 附带 Windows 与 Linux 的 GitHub Actions 测试配置。

## 已知边界

这是轻量语法子集工具，不能完整替代 CommonMark 解析器或 GitHub 渲染器。引用式链接、HTML 链接、自定义 HTML 锚点、目标中的嵌套括号、多行链接、转义方括号及带行内代码的标题尚未完整支持，可能跳过检查或出现锚点误报。外部网址不会联网验证。

仅检查 `.md` 文件中的锚点，其他目标只检查是否存在。路径大小写遵循操作系统行为，因此建议在 Linux CI 中再次检查。空目录会报告检查了 0 个文件。通过检查不代表所有 Markdown 语法都已覆盖。

## 测试与参与

```sh
python -m unittest discover -s tests -v
python docpath.py .
```

详见[英文说明](README.md)、[贡献指南](CONTRIBUTING.md)及 [MIT 许可证](LICENSE)。
