{ pkgs ? import <nixpkgs> {}
}:
let
  python = pkgs.python3.withPackages (ps: with ps; [
    requests
  ]);
in
pkgs.mkShell {
  buildInputs = [
    python
  ];
}
