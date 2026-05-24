# Linux Command Reference

Quick reference for Phase 1 — Systems Engineering Foundations. Commands are grouped by the topics covered in this project: processes, filesystems, shell scripting, and day-to-day backend platform work.

---

## Navigation and Files

| Command  | Purpose                                 | Example                           |
| -------- | --------------------------------------- | --------------------------------- |
| `pwd`    | Print current working directory         | `pwd`                             |
| `cd`     | Change directory                        | `cd /var/log`                     |
| `ls`     | List directory contents                 | `ls -lah`                         |
| `tree`   | Show directory tree (if installed)      | `tree -L 2 src/`                  |
| `find`   | Search for files by name, type, or time | `find . -name "*.yaml" -mtime -7` |
| `locate` | Fast filename lookup (uses indexed DB)  | `locate nginx.conf`               |
| `which`  | Show path to an executable              | `which python3`                   |
| `file`   | Identify file type                      | `file deploy.sh`                  |

**Useful flags**

- `ls -lah` — all files, human-readable sizes, long format
- `find . -type f -size +100M` — files larger than 100 MB
- `find /var/log -name "*.log" -exec tail -n 5 {} \;` — run command on each match

---

## Viewing and Editing Files

| Command         | Purpose                       | Example                                  |
| --------------- | ----------------------------- | ---------------------------------------- |
| `cat`           | Print entire file             | `cat /etc/hosts`                         |
| `less` / `more` | Paginate file output          | `less /var/log/syslog`                   |
| `head` / `tail` | Show start or end of file     | `tail -f app.log`                        |
| `grep`          | Search text patterns          | `grep -r "ERROR" logs/`                  |
| `awk`           | Column/field processing       | `awk '{print $1, $NF}' access.log`       |
| `sed`           | Stream editing / substitution | `sed -i 's/foo/bar/g' config.env`        |
| `wc`            | Count lines, words, bytes     | `wc -l requests.log`                     |
| `sort` / `uniq` | Sort and deduplicate          | `sort access.log \| uniq -c \| sort -nr` |
| `nano` / `vim`  | Terminal text editors         | `vim nginx.conf`                         |

**Common patterns**

```bash
# Follow a log in real time
tail -f /var/log/nginx/access.log

# Search recursively, ignore case, show line numbers
grep -rin "timeout" /etc/nginx/

# Extract the 5 most frequent IP addresses from an access log
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -5
```

---

## Processes and Jobs

| Command              | Purpose                              | Example                     |
| -------------------- | ------------------------------------ | --------------------------- |
| `ps`                 | Snapshot of running processes        | `ps aux`                    |
| `top` / `htop`       | Interactive process monitor          | `htop`                      |
| `pgrep` / `pkill`    | Find or signal processes by name     | `pgrep -a uvicorn`          |
| `kill`               | Send signal to a process             | `kill -15 1234`             |
| `kill -9`            | Force terminate (use sparingly)      | `kill -9 1234`              |
| `nice` / `renice`    | Adjust process priority              | `nice -n 10 ./benchmark.sh` |
| `nohup`              | Run command immune to hangups        | `nohup python app.py &`     |
| `jobs` / `fg` / `bg` | Manage shell background jobs         | `jobs -l`                   |
| `lsof`               | List open files / sockets by process | `lsof -i :8080`             |
| `strace`             | Trace system calls (debugging)       | `strace -p 1234`            |

**Signal cheat sheet**

| Signal    | Number | Meaning                                 |
| --------- | ------ | --------------------------------------- |
| `SIGTERM` | 15     | Graceful shutdown (default for `kill`)  |
| `SIGKILL` | 9      | Immediate termination; cannot be caught |
| `SIGHUP`  | 1      | Hangup; often used to reload config     |
| `SIGINT`  | 2      | Interrupt (Ctrl+C)                      |

**Examples**

```bash
# Find what's listening on port 8000
sudo lsof -iTCP:8000 -sTCP:LISTEN

# Show process tree
ps auxf

# Kill all processes matching a name
pkill -f "uvicorn main:app"
```

---

## System Resources

| Command  | Purpose                     | Example             |
| -------- | --------------------------- | ------------------- |
| `free`   | Memory usage                | `free -h`           |
| `df`     | Disk space by filesystem    | `df -h`             |
| `du`     | Disk usage by directory     | `du -sh /var/log/*` |
| `uptime` | Load averages and uptime    | `uptime`            |
| `vmstat` | Virtual memory statistics   | `vmstat 1 5`        |
| `iostat` | CPU and I/O stats           | `iostat -xz 1`      |
| `dmesg`  | Kernel ring buffer messages | `dmesg \| tail`     |
| `uname`  | System information          | `uname -a`          |
| `lscpu`  | CPU architecture details    | `lscpu`             |
| `lsblk`  | Block devices               | `lsblk`             |

**What to watch on AI/backend hosts**

- **Memory** — model loading and batch inference are memory-heavy (`free -h`, `top`)
- **Disk** — log rotation, model weights, vector index files (`df -h`, `du -sh`)
- **Load** — sustained high load average relative to CPU count (`uptime`, `htop`)
- **Open files** — many concurrent connections can hit ulimit (`lsof`, `ulimit -n`)

---

## Users, Permissions, and Ownership

| Command  | Purpose                  | Example                           |
| -------- | ------------------------ | --------------------------------- |
| `whoami` | Current user             | `whoami`                          |
| `id`     | User and group IDs       | `id`                              |
| `chmod`  | Change file permissions  | `chmod 755 deploy.sh`             |
| `chown`  | Change file owner/group  | `sudo chown app:app /var/log/app` |
| `umask`  | Default permission mask  | `umask`                           |
| `sudo`   | Run command as superuser | `sudo systemctl restart nginx`    |
| `su`     | Switch user              | `su - deploy`                     |

**Permission notation**

```text
rwx rwx rwx
│   │   └── others
│   └────── group
└────────── owner

chmod 644 file   # rw- r-- r--
chmod 755 script # rwx r-x r-x
```

---

## Networking (Linux-side)

| Command                    | Purpose                                              | Example                                  |
| -------------------------- | ---------------------------------------------------- | ---------------------------------------- |
| `ip`                       | Modern network interface/route tool                  | `ip addr show`                           |
| `ifconfig`                 | Legacy interface config (deprecated on many distros) | `ifconfig`                               |
| `ss`                       | Socket statistics (preferred over netstat)           | `ss -tulpn`                              |
| `netstat`                  | Network connections and routing                      | `netstat -tulpn`                         |
| `ping`                     | ICMP reachability test                               | `ping -c 4 api.example.com`              |
| `traceroute` / `tracepath` | Path to destination                                  | `traceroute api.example.com`             |
| `dig`                      | DNS lookup                                           | `dig +short api.example.com`             |
| `nslookup`                 | DNS lookup (simpler)                                 | `nslookup api.example.com`               |
| `host`                     | DNS lookup                                           | `host api.example.com`                   |
| `curl`                     | HTTP/HTTPS client                                    | `curl -I https://api.example.com/health` |
| `wget`                     | Download files over HTTP/FTP                         | `wget https://example.com/file.tar.gz`   |
| `nc` (netcat)              | Test TCP/UDP connectivity                            | `nc -zv localhost 5432`                  |
| `telnet`                   | Legacy port connectivity test                        | `telnet localhost 6379`                  |
| `iptables` / `nft`         | Firewall rules                                       | `sudo iptables -L -n`                    |

**Examples**

```bash
# Check if a port is open locally
ss -tulpn | grep 8080

# Test HTTP endpoint with headers and timing
curl -w "\nDNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTLS: %{time_appconnect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" \
  -o /dev/null -s https://api.example.com/v1/chat

# Resolve DNS with full details
dig api.example.com ANY +noall +answer
```

---

## Filesystem Operations

| Command            | Purpose                               | Example                           |
| ------------------ | ------------------------------------- | --------------------------------- |
| `cp`               | Copy files/directories                | `cp -r src/ backup/src/`          |
| `mv`               | Move or rename                        | `mv app.log app.log.1`            |
| `rm`               | Remove files                          | `rm -rf /tmp/build`               |
| `mkdir`            | Create directory                      | `mkdir -p logs/archive`           |
| `touch`            | Create empty file or update timestamp | `touch .keep`                     |
| `ln`               | Create hard or symbolic links         | `ln -s /data/models ./models`     |
| `tar`              | Archive/compress files                | `tar -czf backup.tar.gz ./config` |
| `gzip` / `gunzip`  | Compress/decompress                   | `gzip large.log`                  |
| `rsync`            | Efficient remote/local sync           | `rsync -avz ./ app@host:/app/`    |
| `mount` / `umount` | Attach/detach filesystems             | `mount \| grep nvme`              |
| `df` / `du`        | Disk usage (see above)                | `du -sh models/`                  |

---

## Package and Service Management

Distro-specific, but these patterns appear constantly in backend work.

### Debian/Ubuntu (`apt`)

```bash
sudo apt update
sudo apt install -y curl jq
apt search nginx
apt show postgresql
```

### RHEL/CentOS/Fedora (`dnf`/`yum`)

```bash
sudo dnf install -y htop
dnf search redis
```

### systemd services

| Command                                | Purpose               |
| -------------------------------------- | --------------------- |
| `systemctl status nginx`               | Check service state   |
| `systemctl start\|stop\|restart nginx` | Control service       |
| `systemctl enable nginx`               | Start on boot         |
| `journalctl -u nginx -f`               | Follow service logs   |
| `systemctl list-units --type=service`  | List running services |

```bash
# Reload nginx config without dropping connections
sudo systemctl reload nginx

# View last 100 lines of a service log since boot
journalctl -u docker -n 100 --no-pager
```

---

## Shell Scripting Essentials

| Construct              | Purpose                            | Example                                   |
| ---------------------- | ---------------------------------- | ----------------------------------------- |
| `#!/bin/bash`          | Shebang — declare interpreter      | First line of scripts                     |
| `$VAR` / `${VAR}`      | Variable expansion                 | `echo $HOME`                              |
| `"$var"`               | Quote variables to preserve spaces | `cp "$src" "$dest"`                       |
| `$1`, `$2`, `$@`       | Positional arguments               | `./deploy.sh staging`                     |
| `$?`                   | Exit code of last command          | `test -f config.yaml \|\| echo "missing"` |
| `\|\|` / `&&`          | OR / AND short-circuit             | `make build && make test`                 |
| `\|`                   | Pipe stdout to next command        | `cat log \| grep ERROR`                   |
| `>`, `>>`, `2>&1`      | Redirect stdout/stderr             | `./app >> app.log 2>&1`                   |
| `$(cmd)`               | Command substitution               | `today=$(date +%F)`                       |
| `if` / `elif` / `else` | Conditional                        | See example below                         |
| `for` / `while`        | Loops                              | See example below                         |
| `function name()`      | Define function                    | See example below                         |
| `set -euo pipefail`    | Strict mode for scripts            | Recommended in production scripts         |
| `trap`                 | Run cleanup on exit/signal         | `trap cleanup EXIT`                       |

**Minimal production-style script**

```bash
#!/usr/bin/env bash
set -euo pipefail

readonly APP_DIR="/opt/myapp"
readonly LOG_FILE="${APP_DIR}/logs/startup.log"

log() {
  echo "[$(date -Iseconds)] $*" | tee -a "$LOG_FILE"
}

main() {
  log "Starting health check..."
  if curl -sf "http://localhost:8080/health" > /dev/null; then
    log "Service is healthy"
  else
    log "Health check failed"
    exit 1
  fi
}

main "$@"
```

---

## Environment and Shell Configuration

| Command        | Purpose                                | Example                     |
| -------------- | -------------------------------------- | --------------------------- |
| `echo $PATH`   | Show executable search path            | `echo $PATH`                |
| `export`       | Set environment variable               | `export API_KEY=secret`     |
| `env`          | Print environment                      | `env \| grep POSTGRES`      |
| `source` / `.` | Load shell script into current session | `source .venv/bin/activate` |
| `alias`        | Command shortcut                       | `alias ll='ls -lah'`        |
| `history`      | Command history                        | `history \| grep docker`    |
| `ulimit`       | Resource limits for shell/process      | `ulimit -n 65535`           |

---

## Docker and Container Debugging (Common in AI Infra)

| Command          | Purpose                      | Example                      |
| ---------------- | ---------------------------- | ---------------------------- |
| `docker ps`      | List running containers      | `docker ps -a`               |
| `docker logs`    | Container stdout/stderr      | `docker logs -f api-1`       |
| `docker exec`    | Run command inside container | `docker exec -it api-1 bash` |
| `docker stats`   | Live resource usage          | `docker stats`               |
| `docker inspect` | Detailed container metadata  | `docker inspect api-1`       |
| `docker compose` | Multi-container local stacks | `docker compose up -d`       |

```bash
# Shell into a running API container
docker exec -it $(docker ps -qf "name=api") bash

# Check which process inside a container holds port 8000
docker exec api-1 ss -tulpn | grep 8000
```

---

## Quick Troubleshooting Playbook

When a backend or model-serving endpoint is slow or failing, this sequence covers most first-pass diagnosis:

```bash
# 1. Is the service running?
systemctl status myapp || docker ps | grep myapp

# 2. Is anything listening on the expected port?
ss -tulpn | grep 8080

# 3. Can you reach it locally?
curl -v http://127.0.0.1:8080/health

# 4. DNS resolving correctly?
dig +short myapp.example.com

# 5. Can you reach it over the network?
curl -I https://myapp.example.com/health

# 6. Check recent logs
journalctl -u myapp -n 200 --no-pager
# or
tail -n 200 /var/log/myapp/app.log

# 7. Resource pressure?
free -h && df -h && uptime
```

---

## Related Deliverables

- [Networking Request Lifecycle Diagram](./diagrams/networking-request-lifecycle.md) — end-to-end path from browser to backend services
- Distributed systems notes _(planned)_
- Architecture breakdowns from _Designing Data-Intensive Applications_ _(planned)_
