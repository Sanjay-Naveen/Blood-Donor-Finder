{ pkgs }: 
pkgs.mkShell rec {
  buildInputs = [
    pkgs.python39
    pkgs.python39Packages.pip
  ];

  shellHook = ''
    export FLASK_APP=app.py
    export FLASK_ENV=development
  '';
}
