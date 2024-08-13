alias b := build
alias rr := rustrun

host := `uname -a`

build:
	cd oauth
	cargo build --manifest-path=oauth/Cargo.toml

rustrun:
	cargo run --manifest-path=oauth/Cargo.toml

server:
	python3 -m server

init:
	python3 -m venv .env
	source .env/bin/activate