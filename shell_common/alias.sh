alias toolbox-enter="SHELL=/bin/zsh toolbox enter"
alias package-search="toolbox run sudo dnf search"

if test -e /run/.toolboxenv
then
  alias ls="exa"
  alias ll="exa -l"
  alias cat="bat"
fi
