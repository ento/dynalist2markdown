{ pkgs ? import <nixpkgs> {}
}:
let
  python = pkgs.python3.withPackages (ps: with ps; [
    pytest
    requests
  ]);
in
pkgs.mkShell {
  buildInputs = [
    python
  ];
}
