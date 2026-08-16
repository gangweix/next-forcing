# Installation

## Next-Forcing Environment

The tested environment uses Python 3.10, PyTorch 2.9.0, and CUDA 12.6.

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install \
  torch==2.9.0 \
  torchvision==0.24.0 \
  torchaudio==2.9.0 \
  --index-url https://download.pytorch.org/whl/cu126
python -m pip install -r requirements.txt --no-build-isolation
```

The post-training dependencies, including LeRobot 0.3.3, are included in
`requirements.txt`.

## RoboTwin Environment

RoboTwin evaluation requires a separate RoboTwin 2.0 environment. The server
and client may use different Python environments, but they must run on the same
machine so the client can connect to the local inference ports.

```bash
git clone https://github.com/RoboTwin-Platform/RoboTwin.git
cd RoboTwin
git checkout 2eeec322
```

Install the Vulkan packages and RoboTwin dependencies, then download the
RoboTwin assets by following the official installation guide:

https://robotwin-platform.github.io/doc/usage/robotwin-install.html

Set the repository location before running an evaluation client:

```bash
export ROBOTWIN_ROOT=/path/to/your/RoboTwin
```

See `README.md` for the training and evaluation commands.
