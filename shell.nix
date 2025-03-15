{ pkgs ? import <nixpkgs> {
    config = {
      permittedInsecurePackages = [
        "olm-3.2.16"
      ];
    };
  }
}:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.pip
    python3Packages.virtualenv
    python3Packages.setuptools
    python3Packages.wheel
  ];

  shellHook = ''
    # Create a virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
      echo "Creating virtual environment..."
      virtualenv venv
    fi
    
    # Activate the virtual environment
    source venv/bin/activate
    
    # Install dependencies
    if ! pip list | grep -q "maubot"; then
      echo "Installing maubot..."
      pip install maubot
    fi
    
    if ! pip list | grep -q "mautrix"; then
      echo "Installing mautrix..."
      pip install mautrix
    fi
    
    if ! pip list | grep -q "python-olm"; then
      echo "Installing python-olm..."
      pip install python-olm
    fi
    
    echo "Development environment ready!"
    echo "To build the plugin: mbc build"
    echo "To test the plugin, you'll need to set up a maubot instance and upload the built .mbp file"
  '';
}
