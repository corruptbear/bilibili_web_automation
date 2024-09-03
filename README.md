# bilibili_web_automation

如果你使用Chrome/Edge/Brave等基于Chromium的浏览器，安装[这个插件](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)

如果你使用Firefox，安装[这个插件](https://addons.mozilla.org/en-US/firefox/addon/get-cookies-txt-locally/)

## 导出私信

使用插件，导出cookie到脚本所在文件夹，保存名称为`message.bilibili.com_cookies.txt`

然后运行脚本

```bash
# xxxxxxxxxx 是你想保存的聊天对象的数字id
# 默认保存为html文件
python3.10 bbot.py xxxxxxxxxx
```