import datetime
import json
import os
import socket
import subprocess


def handle_socket_data(line, config):
    if ("monitoradded" in line) or ("monitorremoved" in line):
        apply_profile(config)


def apply_profile(config):
    hyprctl_monitors = get_hyprctl_monitors()
    for profile in config:
        if set(config[profile]["monitors"].keys()) == hyprctl_monitors:
            print(f"Applying profile: {profile}")
            set_monitors(config[profile]["monitors"])
            set_workspaces(config[profile]["workspaces"])
            return
    print("No matching profile found")


def get_hyprctl_monitors():
    hyprctl_monitors = json.loads(subprocess.run(["hyprctl", "monitors", "-j"], capture_output=True, text=True, check=True).stdout)
    hyprctl_set = {mon["description"] for mon in hyprctl_monitors}
    return hyprctl_set


def set_monitors(monitors):
    lines = []
    for desc, conf in monitors.items():
        line = f"monitor = desc:{desc}, {conf['resolution']}, {conf['position']}, {conf['scale']}"
        if conf['mirror'] is not None:
            line += f", mirror, desc:{conf['mirror']}"
        if conf['transform'] is not None:
            line += f", transform, desc:{conf['transform']}"
        print(line)
        lines.append(line)
    with open(f"{os.environ['HOME']}/.config/hypr/monitors.conf", "w") as f:
        f.write(f"# Generated by myKanshiPlus ({datetime.datetime.now()}). Do not edit manually.\n\n")
        f.write("\n".join(lines))


def set_workspaces(workspaces):
    lines = []
    for ws, rules in workspaces.items():
        line = f"workspace = {ws}, {rules}"
        print(line)
        lines.append(line)
    with open(f"{os.environ['HOME']}/.config/hypr/workspaces.conf", "w") as f:
        f.write(f"# Generated by myKanshiPlus ({datetime.datetime.now()}). Do not edit manually.\n\n")
        f.write("\n".join(lines))


def main():
    with open(f"{os.environ['HOME']}/.config/myKanshiPlus/config.json", "r") as f:
        config = json.load(f)
    apply_profile(config.copy())

    sock_path = f"{os.environ['XDG_RUNTIME_DIR']}/hypr/{os.environ['HYPRLAND_INSTANCE_SIGNATURE']}/.socket2.sock"
    client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        client_socket.connect(sock_path)
        print(f"Connected to {sock_path}")
        while True:
            line = client_socket.recv(1024).decode("utf-8").strip()
            if not line:
                break
            handle_socket_data(line, config.copy())

    except socket.error as e:
        print(f"Socket error: {e}")

    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
