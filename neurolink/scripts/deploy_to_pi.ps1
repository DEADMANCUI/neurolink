param(
    [string]$piUser = "patrickcui",
    [string]$piHost = "192.168.10.160",
    [string]$localDir = "E:\vibe\neurolink",
    [string]$remoteDir = "~/neurolink"
)

Write-Host "Deploying $localDir -> ${piUser}@${piHost}:~"

# Copy project (recursively) to home on Pi
$scp = "scp -r `"$localDir`" ${piUser}@${piHost}:~"
Write-Host $scp
Invoke-Expression $scp

# Ensure Pillow is available on Pi (try apt, then pip fallback)
Write-Host "Installing Pillow on remote (if needed)"
ssh $piUser@$piHost "sudo apt-get update -y && sudo apt-get install -y python3-pil || true"
ssh $piUser@$piHost "python3 -c 'import PIL; print(\"PIL OK\", PIL.__version__)' || pip3 install --user pillow"

# Start the app in Pi desktop session (assumes DISPLAY :0 and XAUTHORITY at ~/.Xauthority)
$startCmd = "export DISPLAY=:0; export XAUTHORITY=/home/${piUser}/.Xauthority; nohup python3 $remoteDir/src/main.py > $remoteDir/run.log 2>&1 & echo $!"
Write-Host "Starting app on Pi..."
ssh $piUser@$piHost $startCmd

Write-Host "Tailing remote run.log (last 200 lines):"
ssh $piUser@$piHost "tail -n 200 $remoteDir/run.log || true"

Write-Host "Done. If GUI doesn't appear, ensure a desktop session is active on the Pi and that XAUTHORITY path is correct."
