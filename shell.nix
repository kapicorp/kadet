# from https://nixos.wiki/wiki/Python#Emulating_virtualenv_with_nix-shell

let
  pkgs = import <nixpkgs> {};

in pkgs.mkShell {
  buildInputs = [
    pkgs.gnumake
    pkgs.act
    pkgs.poetry
    pkgs.nodePackages.yaml-language-server
    pkgs.yamlfix

    /* pkgs.docker */

    # Python version
    pkgs.python39
    pkgs.python39.pkgs.pip

    # Neovim pylsp and tools
    pkgs.python39.pkgs.setuptools
    pkgs.python39.pkgs.pydocstyle
    pkgs.python39.pkgs.python-lsp-server
    pkgs.python39.pkgs.pyls-flake8
    pkgs.python39.pkgs.black
    pkgs.python39.pkgs.isort

    # Tools
    pkgs.python39.pkgs.ipython

  ];

  shellHook = ''
    # Tells pip to put packages into $PIP_PREFIX instead of the usual locations.
    # See https://pip.pypa.io/en/stable/user_guide/#environment-variables.
    export PIP_PREFIX=$(pwd)/_build/pip_packages
    export PYTHONPATH="$PIP_PREFIX/${pkgs.python39.sitePackages}:$PYTHONPATH"
    export PATH="$PIP_PREFIX/bin:$PATH"
    unset SOURCE_DATE_EPOCH
  '';
}
