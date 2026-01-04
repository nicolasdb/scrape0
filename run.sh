#!/bin/bash
# Simple script to scrape any URL with minimal configuration
# Usage: ./run.sh <url> [config.toml]
# Examples:
#   ./run.sh https://openfab.be
#   ./run.sh https://example.com
#   ./run.sh https://example.com ./config/myconfig.toml

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate venv
source "$SCRIPT_DIR/venv/bin/activate"

# Get URL from first argument
if [ -z "$1" ]; then
    echo "Usage: ./run.sh <url> [config.toml]"
    echo ""
    echo "Examples:"
    echo "  ./run.sh https://openfab.be"
    echo "  ./run.sh https://example.com"
    echo "  ./run.sh https://github.com ./config/myconfig.toml"
    echo ""
    exit 1
fi

URL="$1"

# Determine config file
if [ -z "$2" ]; then
    # Auto-detect config based on domain
    # Extract domain from URL
    DOMAIN=$(echo "$URL" | sed 's/https*:\/\///' | sed 's/\/.*$//' | sed 's/www\.//')

    # Check if specific config exists
    if [ -f "$SCRIPT_DIR/config/${DOMAIN}.toml" ]; then
        CONFIG="$SCRIPT_DIR/config/${DOMAIN}.toml"
        echo "✓ Found config for $DOMAIN"
    else
        # Try to find a config that matches
        FOUND_CONFIG=$(grep -l "url_pattern.*${DOMAIN}" "$SCRIPT_DIR"/config/*.toml 2>/dev/null | head -1 || echo "")

        if [ -n "$FOUND_CONFIG" ]; then
            CONFIG="$FOUND_CONFIG"
            echo "✓ Found matching config: $CONFIG"
        else
            # Use default generic config
            CONFIG="$SCRIPT_DIR/config/real-world.toml"
            echo "⚠ Using default config: $(basename $CONFIG)"
            echo "  For better results, create a custom config:"
            echo "  See: ./config/example.toml or ./REAL_URL_TESTING.md"
        fi
    fi
else
    CONFIG="$2"
    if [ ! -f "$CONFIG" ]; then
        echo "✗ Config file not found: $CONFIG"
        exit 1
    fi
fi

echo ""
echo "========================================================================"
echo "Scraping: $URL"
echo "Config:   $(basename $CONFIG)"
echo "========================================================================"
echo ""

# Run the test script
python "$SCRIPT_DIR/test_real_urls.py" "$URL" "$CONFIG"

echo ""
echo "========================================================================"
echo "✓ Done! Output saved to: ./output/real-test.toml"
echo "========================================================================"
