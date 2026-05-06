windows上修改uv cache dir  
进入`%APPDATA%\uv`目录，添加uv.toml文件

```toml
cache-dir = "D:/uv_cache"

[[index]]
url = "https://mirrors.aliyun.com/pypi/simple"
default = true
```