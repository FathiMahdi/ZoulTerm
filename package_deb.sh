#!/bin/bash

set -e  # Exit on error
set -u  # Treat unset variables as error
set -o pipefail

PACKAGE_NAME="zoulterm"
VERSION="0.0.2"
ARCHIVE_NAME="${PACKAGE_NAME}_${VERSION}.deb"
BUILD_DIR="app/${PACKAGE_NAME}_${VERSION}"
OUTPUT_DEB="app/${ARCHIVE_NAME}"

echo "[+] Removing existing installation (if installed)..."
sudo dpkg --remove "${PACKAGE_NAME}" || true

echo "[+] Cleaning up old .deb file..."
rm -f "${OUTPUT_DEB}"

echo "[+] Setting file ownership to root:root..."
sudo chown -R root:root "${BUILD_DIR}"

echo "[+] Fixing directory permissions (0755)..."
find "${BUILD_DIR}" -type d -exec chmod 755 {} \;

echo "[+] Fixing file permissions (0644)..."
find "${BUILD_DIR}" -type f -exec chmod 644 {} \;

echo "[+] Ensuring binary is executable..."
chmod 755 "${BUILD_DIR}/usr/bin/ZoulTerm"

echo "[+] Building .deb package..."
dpkg-deb --build "${BUILD_DIR}" "${OUTPUT_DEB}"

echo "[✓] Package built successfully: ${OUTPUT_DEB}"
