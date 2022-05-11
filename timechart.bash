#!/bin/bash

source $TOOLS/script/use_python3_devel.sh

cd "$(dirname "${BASH_SOURCE[0]}")"

python -m timechart_launcher.main $@
