#!/bin/bash
set -euo pipefail

NAME="livebot"
OWNER="0xM4LL0C"

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m"

LOG_FILE="/tmp/${NAME}_install.log"

say() {
    echo -e "$@" | tee -a "$LOG_FILE"
}

panic() {
    echo -e "${RED}$*${NC}" | tee -a "$LOG_FILE" >&2
    exit 1
}

check_cmd() {
    command -v "$1" > /dev/null 2>&1
}

need_cmd() {
    if ! check_cmd "$1"; then
        panic "need '$1' (command not found)"
    fi
}

main() {
    say "${BLUE}Starting installation of $NAME...${NC}"
    need_cmd curl
    need_cmd tar
    need_cmd install
    need_cmd python3

    say "${YELLOW}Fetching release information...${NC}"
    release_info=$(curl -s "https://api.github.com/repos/$OWNER/$NAME/releases/latest" | tee -a "$LOG_FILE")

    archive_url=$(echo "$release_info" | grep '"tarball_url":' | sed -E 's/.*"([^"]+)".*/\1/')
    tag_name=$(echo "$release_info" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

    say "${YELLOW}Creating temporary directory...${NC}"
    TMP_DIR=$(mktemp -d "$NAME-XXXX" -p /tmp)
    say "Temporary directory created at $TMP_DIR" | tee -a "$LOG_FILE"
    cd "$TMP_DIR"

    say "${YELLOW}Downloading archive...${NC}"
    curl -LJ "$archive_url" -o "$NAME-$tag_name.tar.gz" | tee -a "$LOG_FILE"

    say "${YELLOW}Extracting archive...${NC}"
    tar -zxvf "$NAME-$tag_name.tar.gz" | tee -a "$LOG_FILE"
    unpacked_dir=$(find . -maxdepth 1 -type d -name "$OWNER-$NAME*" | head -n1)

    DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/$NAME"
    say "${YELLOW}Setting up data directory at $DATA_DIR...${NC}"
    mkdir -p "$DATA_DIR"
    rm -rf "$DATA_DIR"/*
    cp -r "$unpacked_dir"/* "$DATA_DIR/" | tee -a "$LOG_FILE"

    BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
    say "${YELLOW}Setting up binary directory at $BIN_DIR...${NC}"
    mkdir -p "$BIN_DIR"
    install "$DATA_DIR/bin/"* "$BIN_DIR/" | tee -a "$LOG_FILE"

    say "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv "$DATA_DIR/.venv" | tee -a "$LOG_FILE"
    $DATA_DIR/.venv/bin/python -m pip install -r "$DATA_DIR/requirements.txt" | tee -a "$LOG_FILE"

    say "${GREEN}Installation of $NAME completed successfully!${NC}"
}

main
