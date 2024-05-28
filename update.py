from pyinfra import host
from pyinfra.facts.server import Path, Which
from pyinfra.operations import apt, server

if host.data.get("type") in {"debian", "proxmox", "ubuntu"}:
    apt.update(name="Apt update")

    apt.upgrade(
        name="Apt upgrade and remove unneeded dependencies",
        auto_remove=True,
    )

    server.shell(
        name="Apt autoremove",
        commands=["apt autoremove"],
    )

    server.shell(
        name="Apt clean",
        commands=["apt clean"],
    )

if host.data.get("type") == "mac":
    env = {"PATH": f"/opt/homebrew/bin:/opt/homebrew/sbin:${host.get_fact(Path)}"}

    server.shell(name="Brew update", commands=["brew update"], _env=env)

    server.shell(name="Brew upgrade", commands=["brew upgrade"], _env=env)

    # server.shell(
    #     name="Brew upgrade casks",
    #     commands=["brew upgrade --cask --greedy"],
    #     _env=env
    # )

    server.shell(name="Brew cleanup", commands=["brew cleanup -s"], _env=env)

    server.shell(
        name="Brew relink",
        commands=[
            "brew list --formula -1 | while read line; do brew unlink $line; brew link $line; done"
        ],
        _env=env,
    )

    server.shell(name="Brew doctor", commands=["brew doctor"], _env=env)

    server.shell(
        name="Write defaults",
        commands=[
            "defaults write com.apple.desktopservices DontWriteNetworkStores -bool true",
            "defaults write com.apple.dock autohide-time-modifier-float 0",
            "defaults write com.apple.dock contents-immutable -bool true",
            "defaults write com.apple.dock ResetLaunchPad -bool true",
            "defaults write com.apple.dock tilesize -int 48",
        ],
    )

    server.shell(name="Restart dock", commands=["killall Dock"])

if host.get_fact(Which, "docker"):
    server.shell(name="Docker prune", commands=["docker system prune -a -f"])
