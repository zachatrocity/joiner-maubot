{
  description = "Maubot Joiner Bot development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          # Allow insecure packages, specifically olm which is needed for Matrix
          config = {
            permittedInsecurePackages = [
              "olm-3.2.16"
            ];
          };
        };
        python = pkgs.python3;
        pythonPackages = python.pkgs;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python
            pythonPackages.pip
            pythonPackages.virtualenv
            pythonPackages.setuptools
            pythonPackages.wheel
            pythonPackages.aiohttp
            pythonPackages.pyyaml
            pythonPackages.click
            pythonPackages.colorama
            pythonPackages.attrs
            pythonPackages.jinja2
            pythonPackages.markdown
            pythonPackages.sqlalchemy
            pythonPackages.ruamel-yaml
            pythonPackages.yarl
            pythonPackages.asyncpg
            pythonPackages.python-olm
            pythonPackages.typing-extensions
            pythonPackages.pillow
          ];

          shellHook = ''
            # Create a virtual environment if it doesn't exist
            if [ ! -d "venv" ]; then
              echo "Creating virtual environment..."
              virtualenv venv
            fi
            
            # Activate the virtual environment
            source venv/bin/activate
            
            # Install maubot and mautrix if not already installed
            if ! pip list | grep -q "maubot"; then
              echo "Installing maubot..."
              pip install maubot
            fi
            
            if ! pip list | grep -q "mautrix"; then
              echo "Installing mautrix..."
              pip install mautrix
            fi
            
            # Alternative approach for users who encounter issues with olm package
            # Uncomment these lines and comment out the pythonPackages.python-olm in buildInputs above
            # if ! pip list | grep -q "python-olm"; then
            #   echo "Installing python-olm..."
            #   pip install python-olm
            # fi
            
            echo "Development environment ready!"
            echo "To build the plugin: mbc build"
            echo "To test the plugin, you'll need to set up a maubot instance and upload the built .mbp file"
          '';
        };
      }
    );
}
