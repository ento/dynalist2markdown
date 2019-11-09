{ pkgs ? import <nixpkgs> {}
}:
let
  python = pkgs.python3.withPackages (ps: with ps; [
    flake8
    pytest
    requests
  ]);
in
pkgs.mkShell {
  buildInputs = [
    python
  ];
}
