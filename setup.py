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
