from pyinfra import host
from pyinfra.facts.docker import DockerContainer, DockerNetwork
from pyinfra.facts.files import File
from pyinfra.facts.server import Command, LsbRelease
from pyinfra.operations import apt, server

if host.data.get("type") in {"debian", "ubuntu"}:
    apt.packages(
        name=f"Install {host.data.get('type')} packages",
        packages=["curl"],
        update=True,
    )

if host.data.get("type") in {"debian", "ubuntu"}:
    dpkg_arch = host.get_fact(Command, command="dpkg --print-architecture")
    lsb_release = host.get_fact(LsbRelease)
    lsb_id = lsb_release["id"].lower()

    if "docker" in host.data.get("tags"):
        apt.packages(
            name="Install docker prerequisites",
            packages=["ca-certificates"],
            update=True,
        )

        apt.key(
            name="Download the docker apt key",
            src=f"https://download.docker.com/linux/{lsb_id}/gpg",
        )

        apt.repo(
            name="Add the docker apt repo",
            filename="docker",
            src=f"deb [arch={dpkg_arch}] https://download.docker.com/linux/{lsb_id} {lsb_release['codename']} stable",
        )

        apt.packages(
            name="Install docker via apt",
            packages=[
                "containerd.io",
                "docker-buildx-plugin",
                "docker-ce",
                "docker-ce-cli",
                "docker-compose-plugin",
            ],
            update=True,
        )

        server.group(
            name="Create docker group",
            group="docker",
        )

        server.user(
            name="Add primary user to docker group",
            groups=["docker"],
            user=host.data.get("username"),
        )

if host.data.get("type") in {"debian", "proxmox", "ubuntu"}:
    dpkg_arch = host.get_fact(Command, command="dpkg --print-architecture")

    apt.deb(
        name="Install cloudflared",
        src=f"https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-{dpkg_arch}.deb",
    )

    if not host.get_fact(File, "/etc/systemd/system/cloudflared.service"):
        server.shell(name="Configure cloudflared", commands=[f"cloudflared service install {host.data.get("cloudflare_tunnel_token")}"])

if "coolify" in host.data.get("tags") and "docker" in host.data.get("tags"):
    if not host.get_fact(DockerNetwork, "coolify"):
        server.shell(name="Add docker network", commands=["docker network create coolify"])

    if not host.get_fact(DockerContainer, "coolify-tailscale"):
        server.shell(
            name="Deploy coolify-tailscale container",
            commands=[
                f"docker run -d -e TS_ACCEPT_DNS=true -e TS_AUTHKEY={host.data.get("tailscale_key")} -e TS_EXTRA_ARGS=--accept-routes -e TS_HOSTNAME={host.data.get("host")}-docker -e TS_USERSPACE=false -v /dev/net/tun:/dev/net/tun --cap-add NET_ADMIN --cap-add NET_RAW --name coolify-tailscale --network coolify tailscale/tailscale"
            ]
        )
