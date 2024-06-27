#!/bin/bash

export X509_USER_PROXY=$HOME/.proxy
# source /gwpool/users/gpizzati/mambaforge/etc/profile.d/conda.sh
# source /gwpool/users/gpizzati/mambaforge/etc/profile.d/mamba.sh
# mamba activate test_uproot

XRD_RUNFORKHANDLER=1

# >>> mamba initialize >>>
# !! Contents within this block are managed by 'mamba init' !!
export MAMBA_EXE='$HOME/.local/bin/micromamba';
export MAMBA_ROOT_PREFIX='$HOME/micromamba';
__mamba_setup="$("$MAMBA_EXE" shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX" 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__mamba_setup"
else
    alias micromamba="$MAMBA_EXE"  # Fallback on help from mamba activate
fi
unset __mamba_setup
# <<< mamba initialize <<<

micromamba activate my_processor
export SPRITZ_PATH=/gwpool/users/gpizzati/test_processor/my_processor
export PYTHONPATH=$SPRITZ_PATH:$PYTHONPATH
