# neurolink

这是名为 neurolink 的工程骨架。

快速开始：

- 创建虚拟环境（可选）： `python -m venv venv`
- 激活虚拟环境（Windows）： `venv\\Scripts\\activate`
- 运行示例： `python src\\main.py`

欢迎告诉我你偏好的语言或框架，我可以继续初始化相应的模板。

树莓派运行说明
----------------

在树莓派 3 上运行示例界面：

1. 确保已安装 Python 3 和 tkinter（一般 Raspbian 自带）。
2. 在项目根目录运行：

```bash
python3 src/main.py
```

按 `Esc` 可以退出全屏（示例实现中使用了全屏模式）。

版本信息保存在 `VERSION` 文件中，程序会在界面左上角显示当前版本号。

部署与 CI
---------

本仓库包含一个 GitHub Actions 工作流 `/.github/workflows/deploy.yml`，可在 `master` 分支推送时自动把代码复制并在目标树莓派上启动应用。为了使自动部署工作，你需要在仓库的 Settings → Secrets 中添加以下 secrets：

- `PI_HOST` — 树莓派 IP 或主机名（例如 `192.168.10.160`）
- `PI_USER` — 登录用户名（例如 `pi` 或你的用户）
- `PI_PORT` — SSH 端口（默认 `22`）
- `PI_SSH_PRIVATE_KEY` — 用于登录的私钥内容（不要使用密码明文）

生成 SSH 密钥对并把公钥追加到树莓派的 `~/.ssh/authorized_keys`：

```bash
ssh-keygen -t ed25519 -C "deploy@github" -f ~/.ssh/neurolink_deploy
ssh-copy-id -i ~/.ssh/neurolink_deploy.pub ${PI_USER}@${PI_HOST}
```

将私钥文件 `~/.ssh/neurolink_deploy` 的内容复制到 `PI_SSH_PRIVATE_KEY` secret 中。

工作流会使用 `appleboy/scp-action` 将仓库文件复制到 `~/neurolink`，并使用 `appleboy/ssh-action` 在目标上运行启动命令（`python3 ~/neurolink/src/main.py`）。如果你的启动命令或路径不同，请在工作流中调整。

手动部署
---------

如果你不使用 CI，可以手动使用脚本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deploy_to_pi.ps1
```

