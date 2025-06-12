{ pkgs }: {
  deps = [
    # Python
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.setuptools
    pkgs.python311Packages.virtualenv
    
    # Node.js
    pkgs.nodejs_20
    pkgs.nodePackages.npm
    pkgs.nodePackages.typescript-language-server
    
    # Databases
    pkgs.postgresql
    pkgs.redis
    
    # System tools
    pkgs.gcc
    pkgs.git
    pkgs.htop
    pkgs.wget
    pkgs.curl
    
    # Process management
    pkgs.supervisor
  ];
  
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
    ];
    PYTHONBIN = "${pkgs.python311}/bin/python3.11";
    LANG = "en_US.UTF-8";
  };
}