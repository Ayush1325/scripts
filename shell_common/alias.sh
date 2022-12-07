alias package-search="toolbox run sudo dnf search"
alias .="source"
alias zola="flatpak run org.getzola.zola"
alias flatpak-builder="flatpak run org.flatpak.Builder"
alias clean-build="cargo clean && cargo build"

if test -e /run/.toolboxenv
then
  eval "$(zoxide init zsh)"
  alias ls="exa"
  alias ll="exa -l"
  alias cat="bat"
  alias cd="z"
  alias find="fd"
fi
